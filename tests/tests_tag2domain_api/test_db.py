import pprint
from unittest import TestCase

import psycopg2

import tag2domain_api.app.util.db
from tag2domain_api.app.util.db import (
    connect_db,
    disconnect_db,
    execute_db,
    set_db,
    get_db,
    get_db_cursor,
    get_db_dict_cursor,
    get_sql_base_table
)

from py_tag2domain.db import Psycopg2Adapter

from tests.util import parse_test_db_config

pprinter = pprint.PrettyPrinter(indent=4)


class DBConnectionTest(TestCase):
    def test_connect_db(self):
        config, _ = parse_test_db_config()
        db_conn = connect_db(config)
        self.assertIsInstance(db_conn, psycopg2.extensions.connection)
        disconnect_db()
        assert tag2domain_api.app.util.db._db_conn is None

    def test_reconnect_db(self):
        config, _ = parse_test_db_config()
        old_db_conn = connect_db(config)
        self.assertIsInstance(old_db_conn, psycopg2.extensions.connection)
        db_conn = connect_db(config)
        self.assertIsInstance(db_conn, psycopg2.extensions.connection)

        self.assertRaisesRegex(
            psycopg2.Error,
            "connection already closed",
            old_db_conn.cursor
        )

        rows = execute_db("SELECT 1;")

        assert len(rows) == 1
        assert rows[0][0] == 1
        disconnect_db()

    def test_connect_db_fails_when_set_db_used(self):
        config, _ = parse_test_db_config()
        old_db_conn = connect_db(config)
        connection_args = Psycopg2Adapter.to_psycopg_args(config)

        conn = psycopg2.connect(**connection_args)
        set_db(conn)

        old_db_conn.close()

        self.assertRaisesRegex(
            ValueError,
            "No config given",
            connect_db
        )

    def test_set_db(self):
        config, _ = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        set_db(conn)

        db_conn = get_db()
        self.assertIsInstance(db_conn, psycopg2.extensions.connection)

        assert tag2domain_api.app.util.db._db_config is None
        assert tag2domain_api.app.util.db._config is None

    def test_get_db_cursor_fails_on_not_connected(self):
        self.assertRaises(RuntimeError, get_db_cursor)

    def test_get_db_cursor(self):
        config, _ = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        set_db(conn)

        cursor = get_db_cursor()
        self.assertIsInstance(cursor, psycopg2.extensions.cursor)
        cursor.execute("SELECT 1;")
        disconnect_db()

    def test_get_db_dict_cursor_fails_on_not_connected(self):
        self.assertRaises(RuntimeError, get_db_dict_cursor)

    def test_get_db_dict_cursor(self):
        config, _ = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        set_db(conn)

        cursor = get_db_dict_cursor()
        self.assertIsInstance(cursor, psycopg2.extensions.cursor)
        cursor.execute("SELECT 1;")
        disconnect_db()

    def test_execute_db_correct_stmt(self):
        config, _ = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        set_db(conn)

        rows = execute_db("SELECT 1;")

        assert len(rows) == 1
        assert rows[0][0] == 1
        disconnect_db()

    def test_execute_db_correct_stmt_on_closed_connection(self):
        config, _ = parse_test_db_config()
        connect_db(config)
        tag2domain_api.app.util.db._db_conn.close()

        rows = execute_db("SELECT 1;")

        assert len(rows) == 1
        assert rows[0][0] == 1
        disconnect_db()

    def test_execute_failing_statement(self):
        config, _ = parse_test_db_config()
        connect_db(config)
        tag2domain_api.app.util.db._db_conn.close()

        self.assertRaises(
            RuntimeError,
            execute_db,
            "SELECT * FROM some_phantasy_table;"
        )

        disconnect_db()

    def test_get_sql_base_table_filter_and_domain_fail(self):
        self.assertRaises(
            ValueError,
            get_sql_base_table,
            "2020-01-01T12:00:00",
            filter="tag=val",
            domain="test.at"
        )

    def test_get_sql_base_table_invalid_filter_fail(self):
        self.assertRaisesRegex(
            ValueError,
            "invalid filter clause - .+",
            get_sql_base_table,
            "2020-01-01T12:00:00",
            filter="_.,"
        )

    def test_get_sql_base_table_filter_by_tag_fail(self):
        self.assertRaisesRegex(
            ValueError,
            "filtering by tags is not implemented",
            get_sql_base_table,
            "2020-01-01T12:00:00",
            filter="taxonomy:tag=value"
        )

    def test_get_sql_base_table_filter_missing_value_fail(self):
        self.assertRaisesRegex(
            ValueError,
            "value is required for filtering by non-tags",
            get_sql_base_table,
            "2020-01-01T12:00:00",
            filter="tag"
        )
