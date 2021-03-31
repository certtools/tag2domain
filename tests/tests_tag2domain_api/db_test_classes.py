from __future__ import print_function

from tag2domain_api.app.util.db import set_db

from tests.util import (
    config as tag2domain_test_config,
    PostgresReadOnlyDBTest,
    PostgresAutoDBTest
)


class APIReadOnlyTest(PostgresReadOnlyDBTest):
    @classmethod
    def setUpClass(cls):
        print("setting up class APIReadOnlyTest")
        super(APIReadOnlyTest, cls).setUpClass()
        cls.no_db_flag = tag2domain_test_config is None
        if not cls.no_db_flag:
            set_db(cls.db_connection)

    @classmethod
    def tearDownClass(cls):
        print("tearing down class APIReadOnlyTest")
        super(APIReadOnlyTest, cls).tearDownClass()

    def setUp(self):
        print("setting up instance of APIReadOnlyTest")
        super(APIReadOnlyTest, self).setUp()


class APIWithAdditionalDBDataTest(PostgresAutoDBTest):
    def setUp(self, *args):
        if len(args) == 0:
            raise ValueError("no DB test cases specified")

        print("setting up instance of APIReadOnlyTest")
        super(APIWithAdditionalDBDataTest, self).setUp()

        for name in args:
            print("loading additional db dataset '%s'" % name)
            self.loadTestCase(name)

        set_db(self.db_connection)


class APIWriteTest(PostgresAutoDBTest):
    def setUp(self):
        print("setting up instance of APIWriteTest")
        super(APIWriteTest, self).setUp()

        set_db(self.db_connection)
