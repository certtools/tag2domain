import os
import logging
import copy
from unittest import TestCase
import binascii

import psycopg2
import psycopg2.sql as sql
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_DEFAULT
)

import tests
from py_tag2domain.util import parse_config
from py_tag2domain.db import Psycopg2Adapter


def parse_test_db_config():
    DB_CONFIG_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config",
        "db.cfg"
    )

    return parse_config(DB_CONFIG_FILE)


config, TypeIntxnTableMappings = parse_test_db_config()
DB_CONNECTION = Psycopg2Adapter.to_psycopg_args(config)


class PostgresReadOnlyDBTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("setting up class PostgresReadOnlyDBTest")
        cls.intxn_table_mappings = TypeIntxnTableMappings
        if DB_CONNECTION is None:
            cls.no_db_flag = True
        else:
            cls.no_db_flag = False
            if isinstance(DB_CONNECTION, str):
                cls.db_connection = psycopg2.connect(DB_CONNECTION)
            elif isinstance(DB_CONNECTION, dict):
                cls.db_connection = psycopg2.connect(**DB_CONNECTION)
            else:
                raise ValueError("DB_CONNECTION must be str or dict")
            cls.db_connection.set_session(readonly=True)
            cls.db_cursor = cls.db_connection.cursor()

    @classmethod
    def tearDownClass(cls):
        print("tearing down class PostgresReadOnlyDBTest")
        if not cls.no_db_flag:
            cls.db_connection.close()

    def setUp(self):
        print("setting up instance of PostgresReadOnlyDBTest")
        if self.__class__.no_db_flag:
            self.skipTest("no db connection specified - skipping DB tests")


def load_test_db_setup(config):
    t2d_db_schema_path = os.path.join(
        "db",
        "00-tag2domain-db-init",
        "sql"
    )
    schema_setup = []
    for name in sorted(os.listdir(t2d_db_schema_path)):
        if not name.endswith(".sql"):
            continue
        _file_path = os.path.join(t2d_db_schema_path, name)
        logging.debug("loading DB schema script from %s" % _file_path)
        _f = open(_file_path)
        schema_setup.append(
            _f
            .read()
            .replace(":t2d_schema", config["DBSCHEMA"])
        )
        _f.close()

    # load the test DB setup script
    t2d_db_test_schema_path = os.path.join(
        os.path.dirname(tests.__file__),
        "db_mock_data",
        "basic",
        "tag2domain_db_test_schema.sql"
    )
    logging.debug("loading DB schema script from %s" % t2d_db_test_schema_path)
    _f = open(t2d_db_test_schema_path)
    schema_setup.append(_f.read())
    _f.close()

    # load the test DB glue script
    t2d_db_test_glue_path = os.path.join(
        os.path.dirname(tests.__file__),
        "db_mock_data",
        "basic",
        "tag2domain_db_test_glue_views.sql"
    )
    logging.debug("loading DB glue script from %s" % t2d_db_test_glue_path)
    _f = open(t2d_db_test_glue_path)
    schema_setup.append(_f.read())
    _f.close()

    schema_setup = ';\n'.join(schema_setup)

    t2d_db_test_data_path = os.path.join(
        os.path.dirname(tests.__file__),
        "db_mock_data",
        "basic",
        "tag2domain_db_test_data.sql"
    )
    logging.debug("loading DB data script from %s" % t2d_db_test_data_path)
    _f = open(t2d_db_test_data_path)
    data_setup = _f.read()

    return schema_setup, data_setup


def setup_test_db(
    connection_args,
    new_db_name,
    base_db_conn,
    base_db_cursor,
    schema_setup,
    data_setup
):
    db_conn = None
    db_cursor = None
    try:
        base_db_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        base_db_cursor.execute(sql.SQL(
            "CREATE DATABASE {}"
        ).format(sql.Identifier(new_db_name,)))
        base_db_conn.set_isolation_level(ISOLATION_LEVEL_DEFAULT)

        # Connect to the new database
        _db_connection = copy.deepcopy(connection_args)
        _db_connection["dbname"] = new_db_name
        db_conn = psycopg2.connect(**_db_connection)

        db_conn.set_session(autocommit=True)
        db_cursor = db_conn.cursor()

        # Run the setup scripts
        db_cursor.execute(schema_setup)
        db_cursor.execute(data_setup)

        db_conn.set_session(autocommit=False)
        # reset the adapter to the new database
        return db_conn, db_cursor
    except Exception:
        # if something goes wrong, reinstate the old DB connection
        # and reraise to propagate the exception to the caller.
        if db_conn is not None:
            logging.debug("closing DB connection (exception)")
            db_conn.close()
        raise


def remove_test_db(db_conn, db_name):
    logging.debug("removing database %s" % db_name)
    db_conn.set_isolation_level(
        ISOLATION_LEVEL_AUTOCOMMIT
    )
    db_conn.cursor().execute(sql.SQL(
        "DROP DATABASE {}"
    ).format(sql.Identifier(db_name,)))
    db_conn.set_isolation_level(
        ISOLATION_LEVEL_DEFAULT
    )


class PostgresAutoDBTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("setting up class PostgresAutoDBTest")
        # load the db setup scripts
        cls.schema_setup, cls.data_setup = load_test_db_setup(config)

        cls.db_prefix = \
            "tag2domain_mock_db_%s" % (binascii.b2a_hex(os.urandom(15)).decode())
        print("prefixing generated DBs by %s" % cls.db_prefix)
        logging.debug("prefixing generated DBs by %s" % cls.db_prefix)
        cls.intxn_table_mappings = TypeIntxnTableMappings

    def setUp(self):
        print("setting up instance of PostgresAutoDBTest")
        if DB_CONNECTION is None:
            self.skipTest("no db connection specified - skipping DB tests")

        if isinstance(DB_CONNECTION, str):
            self.db_connection = psycopg2.connect(DB_CONNECTION)
        elif isinstance(DB_CONNECTION, dict):
            self.db_connection = psycopg2.connect(**DB_CONNECTION)
        else:
            raise ValueError("DB_CONNECTION must be str or dict")

        self.db_cursor = self.db_connection.cursor()

        self.db_name = "%s__%s" % (
            self.__class__.db_prefix,
            self._testMethodName
        )
        logging.debug("creating fresh database %s" % self.db_name)

        self.base_db_conn = self.db_connection
        self.base_db_cursor = self.db_cursor

        try:
            self.db_connection, self.db_cursor = \
                setup_test_db(
                    DB_CONNECTION,
                    self.db_name,
                    self.base_db_conn,
                    self.base_db_cursor,
                    self.__class__.schema_setup,
                    self.__class__.data_setup
                )
        except Exception:
            # reset the db connection and reraise to fail the test
            logging.debug("reset DB connection to base (exception)")
            self.db_connection = self.base_db_conn
            self.db_cursor = self.base_db_cursor

            self.base_db_conn = None
            self.base_db_cursor = None

    def tearDown(self):
        print("tearing down instance of PostgresAutoDBTest")
        # close the database connection and reset the base connection
        if self.base_db_conn is not None:
            logging.debug("close the database connection to the auto DB")
            self.db_connection.close()
            logging.debug("reset DB connection to base")
            self.db_connection = self.base_db_conn
            self.db_cursor = self.base_db_cursor

            # Remove the test database
            assert hasattr(self, 'db_name')
            remove_test_db(self.db_connection, self.db_name)
        else:
            logging.debug("no auto DB handle found")

    def loadTestCase(self, name):
        data_path = os.path.join(
            os.path.dirname(tests.__file__),
            "db_mock_data",
            "test_cases",
            name + ".sql"
        )

        logging.debug("loading test case from %s" % data_path)
        _f = open(data_path)
        data_setup = _f.read()

        self.db_connection.set_session(autocommit=True)
        db_cursor = self.db_connection.cursor()

        # Run the setup scripts
        db_cursor.execute(data_setup)

        self.db_connection.set_session(autocommit=False)
