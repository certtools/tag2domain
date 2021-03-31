from __future__ import print_function

from py_tag2domain.db import Psycopg2Adapter
from tests.util import PostgresReadOnlyDBTest, PostgresAutoDBTest


class PostgresReadOnlyPsycopgAdapterTest(PostgresReadOnlyDBTest):
    @classmethod
    def setUpClass(cls):
        print("setting up class PostgresReadOnlyPsycopgAdapterTest")
        super(PostgresReadOnlyPsycopgAdapterTest, cls).setUpClass()
        cls.adapter = Psycopg2Adapter(
            cls.db_connection,
            cls.intxn_table_mappings
        )

    @classmethod
    def tearDownClass(cls):
        print("tearing down class PostgresReadOnlyPsycopgAdapterTest")
        super(PostgresReadOnlyPsycopgAdapterTest, cls).tearDownClass()

    def setUp(self):
        print("setting up instance of PostgresReadOnlyPsycopgAdapterTest")
        super(PostgresReadOnlyPsycopgAdapterTest, self).setUp()


class PostgresPsycopgAdapterAutoDBTest(PostgresAutoDBTest):
    @classmethod
    def setUpClass(cls):
        print("setting up class PostgresPsycopgAdapterAutoDBTest")
        super(PostgresPsycopgAdapterAutoDBTest, cls).setUpClass()

    def setUp(self):
        print("setting up instance of PostgresPsycopgAdapterAutoDBTest")
        super(PostgresPsycopgAdapterAutoDBTest, self).setUp()
        self.adapter = Psycopg2Adapter(
            self.db_connection,
            self.__class__.intxn_table_mappings
        )

    def tearDown(self):
        print("tearing down instance of PostgresPsycopgAdapterAutoDBTest")
        super(PostgresPsycopgAdapterAutoDBTest, self).tearDown()
