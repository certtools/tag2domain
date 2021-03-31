from __future__ import print_function
import json
import traceback
from unittest import TestCase

from parameterized import parameterized
import psycopg2

from .db_test_classes import (
    PostgresReadOnlyPsycopgAdapterTest,
    PostgresPsycopgAdapterAutoDBTest
)
from py_tag2domain.exceptions import AdapterDBError
from py_tag2domain.util import parse_timestamp
from py_tag2domain.db import Psycopg2Adapter
from tests.util import parse_test_db_config

TAXONOMY_IDS = [
    (1, False, False),
    (2, True, False),
    (3, False, True),
    (4, True, True)
]

TAXONOMY_NAMES = [
    ("tax_test1", 1, False, False),
    ("tax_test2", 2, True, False),
    ("tax_test3", 3, False, True),
    ("tax_test4", 4, True, True)
]

EXISTING_TAGS = [
    (1, [1, 2, 3]),
    (3, [4, ]),
    (1, [1, 3]),
    (3, []),
]

TAG_NAMES = [
    (1, ["test_tag_1_tax_1", "test_tag_2_tax_1", "test_tag_3_tax_1"], [1, 2, 3]),
    (1, ["test_tag_1_tax_1", "test_tag_3_tax_1"], [1, 3]),
    (1, ["test_tag_1_tax_1", "test_tag_1_tax_127"], [1, None]),
    (3, ["test_tag_1_tax_3", ], [4, ]),
    (3, [], []),
]

EXISTING_VALUES = [
    ([(1, 1), (1, 2)], ),
    ([(1, 1), ], ),
    ([(4, 3), ], ),
]

VALUE_NAMES = [
    ([(1, "value_1_tag_1",), (1, "value_2_tag_1",)], [1, 2]),
    ([(4, "value_1_tag_4",), ], [3, ]),
    ([(4, "value_1_tag_4",), (2, "value_189_tag_2")], [3, None, ]),
    ([(1, "value_1_tag_1",), (1, "value_189_tag_2",)], [1, None]),
    ([(138, "value_1_tag_4",), ], [None, ]),
]

TEST_INSERT_TAGS = [
    ([],),
    ([
        {
            "tag_name": "test_insert_tag_1",
            "tag_description": "test tag insert 1",
            "taxonomy_id": 1,
            "extras": "{}"
        }
    ],),
    ([
        {
            "tag_name": "test_insert_tag_2",
            "tag_description": "test tag insert 2",
            "taxonomy_id": 3,
            "extras": '{"some_extra_value":42}'
        },
        {
            "tag_name": "test_insert_tag_3",
            "tag_description": "test tag insert 3",
            "taxonomy_id": 4,
            "extras": '{}'
        }
    ],),
    ([  # extras field is missing - should go through
        {
            "tag_name": "test_insert_tag_4",
            "tag_description": "test tag insert 4",
            "taxonomy_id": 4
        }
    ],)
]

TEST_INSERT_TAGS_INVALID = [
    ([  # taxonomy does not exist
        {
            "tag_name": "test_insert_tag_1",
            "tag_description": "test tag insert 1",
            "taxonomy_id": 56,
            "extras": "{}"
        }
    ],),
    ([  # missing tag description
        {
            "tag_name": "test_insert_tag_2",
            "taxonomy_id": 3,
            "extras": '{"some_extra_value":42}'
        }
    ],),
    ([  # missing taxonomy_id
        {
            "tag_name": "test_insert_tag_3",
            "tag_description": "test tag insert 3",
            "extras": '{"some_extra_value":42}'
        }
    ],)
]

TEST_INSERT_VALUES = [
    ([],),
    ([
        {
            "value": "inserted_value_1",
            "tag_id": 3
        },
        {
            "value": "inserted_value_2",
            "tag_id": 4
        }
    ],)
]

TEST_INSERT_VALUES_INVALID = [
    ([
        {
            "value": "inserted_value_3",
            "tag_id": 189
        },
    ],)
]

_, INTXN_TABLE_MAPPINGS = parse_test_db_config()


class Psycopg2AdapterStaticTest(TestCase):
    def test_psycopg_args_with_null_returns_null(self):
        self.assertIsNone(Psycopg2Adapter.to_psycopg_args(None))

    def test_psycopg_invalid_args_fail(self):
        self.assertRaises(
            ValueError,
            Psycopg2Adapter.to_psycopg_args,
            {}
        )

    def test_psycopg2_args_dict(self):
        config, intxn_table_map = parse_test_db_config()
        adapter = Psycopg2Adapter(
            Psycopg2Adapter.to_psycopg_args(config),
            intxn_table_map
        )
        adapter.db_connection.cursor().execute("SELECT 1")

    def test_psycopg2_args_string(self):
        config, intxn_table_map = parse_test_db_config()
        args_dict = Psycopg2Adapter.to_psycopg_args(config)
        args_list = [
            "%s=%s" % (key, val)
            for key, val in args_dict.items()
            if key != "options"
        ]
        args = ' '.join(args_list)
        print(args)
        adapter = Psycopg2Adapter(args, intxn_table_map)
        adapter.db_connection.cursor().execute("SELECT 1")

    def test_psycopg2_args_invalid_config_fail(self):
        config, intxn_table_map = parse_test_db_config()
        self.assertRaisesRegex(
            ValueError,
            "unknown datatype for connect_params - expect dict or str, got .+",
            Psycopg2Adapter,
            1,
            intxn_table_map
        )

    def test_psycopg2_args_autocommmit_conn_fail(self):
        config, intxn_table_map = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        conn.set_session(autocommit=True)

        self.assertRaisesRegex(
            ValueError,
            "DB connection used must not be in in autocommit mode",
            Psycopg2Adapter,
            conn,
            intxn_table_map
        )

    def test_get_stmt_unknown_type_fail(self):
        config, intxn_table_map = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        adapter = Psycopg2Adapter(conn, intxn_table_map)
        self.assertRaises(
            AdapterDBError,
            adapter.get_compiled_stmt,
            "get_open_tags",
            "some unknown type"
        )

    def test_get_stmt_unknown_stmt_fail(self):
        config, intxn_table_map = parse_test_db_config()
        connection_args = Psycopg2Adapter.to_psycopg_args(config)
        conn = psycopg2.connect(**connection_args)
        adapter = Psycopg2Adapter(conn, intxn_table_map)
        self.assertRaises(
            ValueError,
            adapter.get_compiled_stmt,
            "some unknown stmt",
            "domain"
        )


class Psycopg2AdapterReadOnlyTest(PostgresReadOnlyPsycopgAdapterTest):

    @parameterized.expand(TAXONOMY_IDS)
    def test_fetch_taxonomy_by_id(
        self,
        taxonomy_id,
        allows_auto_tags,
        allows_auto_values
    ):
        taxonomy = Psycopg2AdapterReadOnlyTest.adapter.fetch_taxonomy_by_id(taxonomy_id)

        self.assertEqual(taxonomy["allows_auto_tags"], allows_auto_tags)
        self.assertEqual(taxonomy["allows_auto_values"], allows_auto_values)

    def test_fetch_non_existing_taxonomy_by_id(self):
        self.assertRaises(
            AdapterDBError,
            Psycopg2AdapterReadOnlyTest.adapter.fetch_taxonomy_by_id,
            23876975
        )

    @parameterized.expand(TAXONOMY_NAMES)
    def test_fetch_taxonomy_by_name(
        self,
        taxonomy_name,
        id,
        allows_auto_tags,
        allows_auto_values
    ):
        taxonomy = Psycopg2AdapterReadOnlyTest.adapter.fetch_taxonomy_by_name(taxonomy_name)

        self.assertEqual(taxonomy["id"], id)
        self.assertEqual(taxonomy["allows_auto_tags"], allows_auto_tags)
        self.assertEqual(taxonomy["allows_auto_values"], allows_auto_values)

    def test_fetch_non_existing_taxonomy_by_name(self):
        self.assertRaises(
            AdapterDBError,
            Psycopg2AdapterReadOnlyTest.adapter.fetch_taxonomy_by_name,
            "non_existing_taxonomy"
        )

    @parameterized.expand(EXISTING_TAGS)
    def test_check_tag_ids_exist_on_existing(self, taxonomy_id, tag_id_list):
        try:
            Psycopg2AdapterReadOnlyTest.adapter.check_tag_ids_exist(taxonomy_id, tag_id_list)
        except AdapterDBError:
            self.fail(
                "check_tag_ids_exist raised AdapterDBError on existing tag"
            )

    def test_check_tag_ids_exist_on_non_existing(self):
        self.assertRaises(
            AdapterDBError,
            Psycopg2AdapterReadOnlyTest.adapter.check_tag_ids_exist,
            1,
            [198, ]
        )

    @parameterized.expand(TAG_NAMES)
    def test_fetch_tag_ids_by_name(
        self,
        taxonomy_id,
        tag_name_list,
        ids_to_fetch
    ):
        tag_ids = Psycopg2AdapterReadOnlyTest.adapter.fetch_tag_ids_by_name(taxonomy_id, tag_name_list)
        self.assertDictEqual(tag_ids, dict(zip(tag_name_list, ids_to_fetch)))

    @parameterized.expand(EXISTING_VALUES)
    def test_check_value_ids_exist_on_existing(self, value_ids):
        try:
            Psycopg2AdapterReadOnlyTest.adapter.check_value_ids_exist(value_ids)
        except AdapterDBError:
            self.fail(
                "check_value_ids_exist raised AdapterDBError on existing value"
            )

    def test_check_value_ids_exist_on_non_existing(self):
        self.assertRaises(
            AdapterDBError,
            Psycopg2AdapterReadOnlyTest.adapter.check_value_ids_exist,
            [(198, 172), ]
        )

    @parameterized.expand(VALUE_NAMES)
    def test_fetch_value_ids_by_value(
        self,
        value_list,
        ids_to_fetch
    ):
        value_ids = Psycopg2AdapterReadOnlyTest.adapter.fetch_value_ids_by_value(value_list)
        self.assertDictEqual(value_ids, dict(zip(value_ids, ids_to_fetch)))

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_get_open_tags(self, tag_type):
        def check_tag_is_present(tag, list_):
            for i in range(len(list_)):
                _tag = list_[i]
                self.assertTrue("tag_id" in _tag)
                self.assertTrue("value_id" in _tag)
                self.assertTrue("measured_at" in _tag)
                self.assertTrue("producer" in _tag)
                if (
                    (tag["tag_id"] == _tag["tag_id"])
                    and (tag["value_id"] == _tag["value_id"])
                ):
                    list_.pop(i)
                    return True
            assert False, "tag %s not present" % str(tag)

        open_tags = self.adapter.get_open_tags(
            1,  # taxonomy_id
            tag_type,
            1
        )
        check_tag_is_present({"tag_id": 1, "value_id": None}, open_tags)
        check_tag_is_present({"tag_id": 2, "value_id": None}, open_tags)
        self.assertEqual(len(open_tags), 0)

        open_tags = self.adapter.get_open_tags(
            1,  # taxonomy_id
            tag_type,
            2
        )
        check_tag_is_present({"tag_id": 1, "value_id": 1}, open_tags)
        self.assertEqual(len(open_tags), 0)

        open_tags = self.adapter.get_open_tags(
            3,  # taxonomy_id
            tag_type,
            1
        )
        check_tag_is_present({"tag_id": 4, "value_id": None}, open_tags)
        self.assertEqual(len(open_tags), 0)


class Psycopg2AdapterWriteTest(PostgresPsycopgAdapterAutoDBTest):
    @parameterized.expand(TEST_INSERT_TAGS)
    def test_insert_tags_valid(self, tag_list):
        tag_ids = self.adapter.insert_tags(tag_list)
        self.adapter.commit()
        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )
        for _tag in tag_list:
            _id = tag_ids[_tag["tag_name"]]
            cursor.execute(
                """
                SELECT * FROM tags WHERE tag_id = %s
                """,
                (_id,)
            )
            _row = cursor.fetchone()

            # only a single row should be returned
            self.assertEqual(cursor.fetchone(), None)

            self.assertEqual(_row["tag_name"], _tag["tag_name"])
            self.assertEqual(_row["tag_description"], _tag["tag_description"])
            self.assertEqual(_row["taxonomy_id"], _tag["taxonomy_id"])
            if "extras" in _tag:
                self.assertDictEqual(
                    json.loads(_tag["extras"]),
                    json.loads(_row["extras"])
                )
            else:
                self.assertEqual(_row["extras"], {})

    @parameterized.expand(TEST_INSERT_TAGS_INVALID)
    def test_insert_tags_invalid(self, tag_list):
        self.assertRaises(
            AdapterDBError,
            self.adapter.insert_tags,
            tag_list
        )

    @parameterized.expand(TEST_INSERT_VALUES_INVALID)
    def test_insert_values_invalid(self, value_list):
        self.assertRaises(
            AdapterDBError,
            self.adapter.insert_values,
            value_list
        )

    @parameterized.expand(TEST_INSERT_VALUES)
    def test_insert_values(self, value_list):
        value_ids = self.adapter.insert_values(value_list)
        self.adapter.commit()
        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )
        for _value in value_list:
            self.assertTrue((_value["value"], _value["tag_id"]) in value_ids)
            _id = value_ids[(_value["value"], _value["tag_id"])]
            cursor.execute(
                """
                SELECT * FROM taxonomy_tag_val WHERE id = %s
                """,
                (_id,)
            )
            _row = cursor.fetchone()
            self.assertIsNotNone(_row)

            # only a single row should be returned
            self.assertIsNone(cursor.fetchone())

            assert _row["value"] == _value["value"]
            assert _row["tag_id"] == _value["tag_id"]

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_insert_intersection_no_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        try:
            self.adapter.insert_intersections(
                1,
                timestamp,
                [
                    {
                        "tag_id": 1,
                        "value_id": None
                    }
                ],
                tag_type,
                3,
                producer="test_producer"
            )
        except Exception as e:
            traceback.print_exc()
            self.fail("insert_intersections raised exception '%s'" % type(e))

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 3
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["start_ts"], timestamp)
        self.assertEqual(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertEqual(_row["producer"], "test_producer")

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_insert_intersection_with_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.insert_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": 2
                }
            ],
            tag_type,
            3
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 3
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s = 2)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["start_ts"], timestamp)
        self.assertEqual(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_insert_multiple_intersections(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.insert_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": 2
                },
                {
                    "tag_id": 3,
                    "value_id": None
                }
            ],
            tag_type,
            3
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 3
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s = 2)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["start_ts"], timestamp)
        self.assertEqual(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 3
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 3)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["start_ts"], timestamp)
        self.assertEqual(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_prolong_intersection_no_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.prolong_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ],
            tag_type,
            1
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_prolong_intersection_no_value_change_producer(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.prolong_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ],
            tag_type,
            1,
            producer="test_producer_modified"
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertEqual(_row["producer"], "test_producer_modified")

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_prolong_intersection_with_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.prolong_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": 1
                }
            ],
            tag_type,
            2
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at
            FROM %(table_name)s
            WHERE
                %(id)s = 2
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s = 1)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_prolong_multiple_intersections(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.prolong_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                },
                {
                    "tag_id": 2,
                    "value_id": None
                }
            ],
            tag_type,
            1
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(measured_at)s AS measured_at
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 2)
                AND (%(value_id)s IS NULL)
                AND (%(end_date)s IS NULL)
                AND (%(end_ts)s IS NULL)
            """ % intxn_mappings
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_end_intersection_no_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.end_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ],
            tag_type,
            1
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_ts)s = %%s)
            """ % intxn_mappings,
            (timestamp,)
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["end_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_end_intersection_no_value_change_producer(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.end_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ],
            tag_type,
            1,
            producer="test_producer_modified"
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_ts)s = %%s)
            """ % intxn_mappings,
            (timestamp,)
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())
        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["end_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertEqual(_row["producer"], "test_producer_modified")

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_end_intersection_with_value(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.end_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": 1
                }
            ],
            tag_type,
            2
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 2
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s = 1)
                AND (%(end_ts)s = %%s)
            """ % intxn_mappings,
            (timestamp,)
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["end_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_end_multiple_intersections(self, tag_type):
        timestamp = parse_timestamp("2020-09-30T12:34:21.9855")
        intxn_mappings = INTXN_TABLE_MAPPINGS[tag_type]
        self.adapter.end_intersections(
            1,
            timestamp,
            [
                {
                    "tag_id": 1,
                    "value_id": None
                },
                {
                    "tag_id": 2,
                    "value_id": None
                }
            ],
            tag_type,
            1
        )

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 1)
                AND (%(value_id)s IS NULL)
                AND (%(end_ts)s = %%s)
            """ % intxn_mappings,
            (timestamp,)
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["end_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])

        cursor.execute(
            """
            SELECT
                %(start_ts)s AS start_ts,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND (%(taxonomy_id)s = 1)
                AND (%(tag_id)s = 2)
                AND (%(value_id)s IS NULL)
                AND (%(end_ts)s = %%s)
            """ % intxn_mappings,
            (timestamp,)
        )

        _row = cursor.fetchone()
        self.assertIsNotNone(_row)

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertLess(_row["start_ts"], timestamp)
        self.assertLess(_row["start_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["end_date"], int(timestamp.strftime("%Y%m%d")))
        self.assertEqual(_row["measured_at"], timestamp)
        self.assertIsNone(_row["producer"])
