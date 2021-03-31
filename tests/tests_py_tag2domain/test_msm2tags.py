from unittest import TestCase
import pprint
import datetime
import traceback
from types import MappingProxyType

from parameterized import parameterized
import psycopg2.extras
import psycopg2.tz
import json

from py_tag2domain.msm2tags import MeasurementToTags
from py_tag2domain.exceptions import (
    InvalidMeasurementException,
    DisallowedTaxonomyModificationException,
    StaleMeasurementException
)
from py_tag2domain.util import parse_timestamp
from tests.util import parse_test_db_config
from .db_test_classes import (
    PostgresReadOnlyPsycopgAdapterTest,
    PostgresPsycopgAdapterAutoDBTest
)

FAILING_MEASUREMENTS = [
    [{}, ],
    [{  # missing keys
        "tag_type": "whatever",
    }, ],
    [{  # taxonomy wrong datatype
        "tag_type": "domain",
        "taxonomy": 72.651,
        "tagged_id": 5247
    }, ],
    [{  # missing version
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de"
            },
            {
                "tag": "en"
            },
        ]
    }, ],
    [{
        "version": "1",
        "tag_type": "domain",
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de"
            },
            {
                "tag": "en"
            },
        ]
    }, ],
    [{  # missing tag specs with autogenerate_tags
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de",
                "value": "comment",
                "extras": {"version": "1"}
            },
            {
                "tag": "en",
                "description": "german",
                "extras": {"version": "1"}
            },
        ],
        "autogenerate_tags": True
    }, ],
    [{  # incorrect timestamp
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27 19:35:32.982305",
        "tags": [
            {
                "tag": "de"
            },
            {
                "tag": "en"
            },
        ]
    }, ],
    [{  # tag given as name with autogenerate_true
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": 23,
                "description": "german",
                "extras": {"version": "1"}
            }
        ],
        "autogenerate_tags": True
    }, ],
]

CORRECT_MEASUREMENTS = [
    [{
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de"
            },
            {
                "tag": "en"
            },
        ]
    }, ],
    [{  # timestamp without fractionas of a second
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32",
        "tags": [
            {
                "tag": "de"
            },
            {
                "tag": "en"
            },
        ]
    }, ],
    [{
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": 1
            },
            {
                "tag": 2
            },
        ]
    }, ],
    [{
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de",
                "value": "comment"
            }
        ],
        "autogenerate_values": True
    }, ],
    [{  # tag value given by ID
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de",
                "value": 27
            }
        ],
        "autogenerate_values": True
    }, ],
    [{
        "version": "1",
        "tag_type": "domain",
        "tagged_id": 5247,
        "taxonomy": "language",
        "producer": "test",
        "measured_at": "2020-09-27T19:35:32.982305",
        "tags": [
            {
                "tag": "de",
                "description": "german",
                "extras": {"version": "v1"}
            }
        ],
        "autogenerate_tags": True
    }, ],
]

_, INTXN_TABLE_MAPPINGS = parse_test_db_config()
for _type in INTXN_TABLE_MAPPINGS.keys():
    INTXN_TABLE_MAPPINGS[_type]["__fields__"] = ',\n'.join([
        "%s AS %s" % (value, key)
        for key, value in INTXN_TABLE_MAPPINGS[_type].items()
    ])


class MeasurementValidationTest(TestCase):
    def setUp(self):
        self.msm_to_tags = MeasurementToTags(None)

    @parameterized.expand(FAILING_MEASUREMENTS)
    def test_failing_measurement(self, msm):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.validate_measurement,
            msm
        )

    @parameterized.expand(CORRECT_MEASUREMENTS)
    def test_correct_measurement(self, msm):
        try:
            self.msm_to_tags.validate_measurement(msm)
        except Exception as e:
            traceback.print_exc()
            self.fail("unexpected exception - %s" % str(e))


class HandleMeasurementTaxonomyModsNoInsertTest(PostgresPsycopgAdapterAutoDBTest):
    def setUp(self):
        super(HandleMeasurementTaxonomyModsNoInsertTest, self).setUp()
        self.msm_to_tags = MeasurementToTags(self.adapter)

    def tearDown(self):
        super(HandleMeasurementTaxonomyModsNoInsertTest, self).tearDown()

    def test_check_existing_ids_exist(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1,
                        "value": 1
                    },
                    {
                        "tag": 2
                    },
                ]
            }
        )
        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 1,
                    'allows_auto_tags': False,
                    'allows_auto_values': False
                },
                'tags': [
                    {'tag': 1, 'tag_id': 1, "value": 1, "value_id": 1},
                    {'tag': 2, 'tag_id': 2}
                ]
            }
        )

    def test_check_non_existing_taxonomy_id_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 6548,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1,
                        "value": 1
                    },
                    {
                        "tag": 2
                    },
                ]
            }
        )

    def test_check_non_existing_tag_id_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 5646874,
                        "value": 1
                    },
                    {
                        "tag": 2
                    },
                ]
            }
        )

    def test_check_non_existing_value_id_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1,
                        "value": 1
                    },
                    {
                        "tag": 15676348
                    },
                ]
            }
        )

    def test_check_non_existing_tag_value_pair_by_id_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 2,
                        "value": 1
                    },
                    {
                        "tag": 1
                    },
                ]
            }
        )

    def test_check_tag_from_different_taxonomy_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 4
                    }
                ]
            }
        )

    def test_check_tag_by_name_value_by_id(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "test_tag_1_tax_1",
                        "value": 1
                    },
                    {
                        "tag": "test_tag_2_tax_1"
                    },
                ]
            }
        )

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 1,
                    'allows_auto_tags': False,
                    'allows_auto_values': False
                },
                'tags': [
                    {
                        'tag': 'test_tag_1_tax_1',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1',
                        "value": 1,
                        "value_id": 1
                    },
                    {
                        'tag': 'test_tag_2_tax_1',
                        'tag_name': 'test_tag_2_tax_1',
                        'tag_id': 2
                    }
                ]
            }
        )

    def test_check_tag_by_name_value_by_name(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "test_tag_1_tax_1",
                        "value": "value_2_tag_1"
                    }
                ]
            }
        )

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 1,
                    'allows_auto_tags': False,
                    'allows_auto_values': False
                },
                'tags': [
                    {
                        'tag': 'test_tag_1_tax_1',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1',
                        "value": "value_2_tag_1",
                        "value_id": 2
                    }
                ]
            }
        )

    def test_check_insert_tag_in_protected_fails(self):
        self.assertRaises(
            DisallowedTaxonomyModificationException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "some_new_tag_67337"
                    }
                ],
                "autogenerate_tags": True
            }
        )

    def test_check_unknown_tag_without_auto_flag_fails(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "some_new_tag_67337"
                    }
                ]
            }
        )

    def test_check_insert_value_in_protected_fails(self):
        self.assertRaises(
            DisallowedTaxonomyModificationException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1,
                        "value": "some_new_value"
                    }
                ],
                "autogenerate_values": True
            }
        )

    def test_check_unknown_value_without_auto_flag(self):
        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.prepare_tag2domain_taxonomy,
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 1,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1,
                        "value": "some_new_value"
                    }
                ]
            }
        )

    def test_check_taxonomy_by_name(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": "tax_test1",
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 1
                    }
                ]
            }
        )

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 1,
                    'allows_auto_tags': False,
                    'allows_auto_values': False
                },
                'tags': [
                    {
                        'tag': 1,
                        'tag_id': 1
                    }
                ]
            }
        )


class HandleMeasurementTaxonomyModsWithInsertTest(PostgresPsycopgAdapterAutoDBTest):
    def setUp(self):
        super(HandleMeasurementTaxonomyModsWithInsertTest, self).setUp()
        self.msm_to_tags = MeasurementToTags(self.adapter)

    def test_check_db_info_insert_new_tag(self):
        db_info = self.msm_to_tags.fetch_db_information(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": "tax_test2",
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "new_tag_tax_2"
                    }
                ],
                "autogenerate_tags": True
            }
        )

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 2,
                    'allows_auto_tags': True,
                    'allows_auto_values': False
                },
                'tags': [
                    {
                        'tag': 'new_tag_tax_2',
                        'tag_name': 'new_tag_tax_2',
                        'tag_id': None
                    }
                ]
            }
        )

    def test_check_db_info_insert_new_value(self):
        db_info = self.msm_to_tags.fetch_db_information(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 3,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 4,
                        "value": "some_new_value"
                    }
                ],
                "autogenerate_values": True
            }
        )

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 3,
                    'allows_auto_tags': False,
                    'allows_auto_values': True
                },
                'tags': [
                    {
                        'tag': 4,
                        'tag_id': 4,
                        'value': "some_new_value",
                        'value_id': None
                    }
                ]
            }
        )

    def test_check_insert_new_tag(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 2,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": "some_new_tag",
                        "description": "some fresh tag",
                        "extras": {
                            "some_additional_info": "whatever"
                        }
                    }
                ],
                "autogenerate_tags": True
            }
        )

        DUMMY_VALUE = 9999999999
        self.assertEqual(len(db_info["tags"]), 1)
        self.assertTrue("tag_id" in db_info["tags"][0])
        self.assertIsInstance(db_info["tags"][0]["tag_id"], int)
        _id = db_info["tags"][0]["tag_id"]
        db_info["tags"][0]["tag_id"] = DUMMY_VALUE

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 2,
                    'allows_auto_tags': True,
                    'allows_auto_values': False
                },
                'tags': [
                    {
                        'tag': "some_new_tag",
                        'tag_id': DUMMY_VALUE,
                        'tag_description': "some fresh tag",
                        'tag_name': "some_new_tag",
                        "extras": {
                            "some_additional_info": "whatever"
                        }
                    }
                ]
            }
        )

        self.adapter.commit()
        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT * FROM tags WHERE tag_id = %s
            """,
            (_id,)
        )
        _row = cursor.fetchone()

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["tag_name"], "some_new_tag")
        self.assertEqual(_row["tag_description"], "some fresh tag")
        self.assertEqual(_row["taxonomy_id"], 2)
        self.assertDictEqual(
            _row["extras"],
            json.loads('{ "some_additional_info": "whatever"}')
        )

    def test_check_insert_new_value(self):
        db_info = self.msm_to_tags.prepare_tag2domain_taxonomy(
            {
                "version": "1",
                "tag_type": "domain",
                "tagged_id": 5247,
                "taxonomy": 3,
                "producer": "test",
                "measured_at": "2020-09-27T19:35:32.982305",
                "tags": [
                    {
                        "tag": 4,
                        "value": "some_new_value"
                    }
                ],
                "autogenerate_values": True
            }
        )

        DUMMY_VALUE = 9999999999
        self.assertEqual(len(db_info["tags"]), 1)
        self.assertTrue("value_id" in db_info["tags"][0])
        self.assertIsInstance(db_info["tags"][0]["value_id"], int)
        _id = db_info["tags"][0]["value_id"]
        db_info["tags"][0]["value_id"] = DUMMY_VALUE

        self.assertDictEqual(
            db_info,
            {
                'taxonomy': {
                    'id': 3,
                    'allows_auto_tags': False,
                    'allows_auto_values': True
                },
                'tags': [
                    {
                        'tag': 4,
                        'tag_id': 4,
                        'value': "some_new_value",
                        'value_id': DUMMY_VALUE
                    }
                ]
            }
        )

        self.adapter.commit()
        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        cursor.execute(
            """
            SELECT * FROM taxonomy_tag_val WHERE id = %s
            """,
            (_id,)
        )
        _row = cursor.fetchone()

        # only a single row should be returned
        self.assertIsNone(cursor.fetchone())

        self.assertEqual(_row["value"], "some_new_value")
        self.assertEqual(_row["tag_id"], 4)


class HandleMeasurementCalcChangesTest(PostgresReadOnlyPsycopgAdapterTest):
    @classmethod
    def setUpClass(cls):
        super(HandleMeasurementCalcChangesTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(HandleMeasurementCalcChangesTest, cls).tearDownClass()

    def setUp(self):
        super(HandleMeasurementCalcChangesTest, self).setUp()
        print("setting up MeasurementToTags instance")
        self.msm_to_tags = MeasurementToTags(__class__.adapter)
        print("testing connection")
        self.msm_to_tags.db_adapter.db_cursor.execute("SELECT 1")

    def tearDown(self):
        print("tearing down MeasurementToTags instance")

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_empty_tags(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": []
        }

        changes = self.msm_to_tags.calculate_changes(
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "test_producer1",
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (),
                "prolong": (),
                "end": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                    MeasurementToTags.TagStateTuple(tag_id=2, value_id=None)
                )
            }
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_empty_tags_fails_none_producer(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": []
        }

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.calculate_changes,
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            None,
            taxonomy_db_info
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_empty_tags_fails_other_producer(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": []
        }

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.calculate_changes,
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "different_test_producer",
            taxonomy_db_info
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_new_tag_no_val_closing_others(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": [
                {
                    "tag_id": 5,
                    "value_id": None
                }
            ]
        }

        changes = self.msm_to_tags.calculate_changes(
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "test_producer1",
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (
                    MeasurementToTags.TagStateTuple(tag_id=5, value_id=None),
                ),
                "prolong": (),
                "end": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                    MeasurementToTags.TagStateTuple(tag_id=2, value_id=None)
                )
            }
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_new_tag_no_val_prolonging_others(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": [
                {
                    "tag_id": 1,
                    "value_id": None
                },
                {
                    "tag_id": 2,
                    "value_id": None
                },
                {
                    "tag_id": 5,
                    "value_id": None
                }
            ]
        }

        changes = self.msm_to_tags.calculate_changes(
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "test_producer1",
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (
                    MeasurementToTags.TagStateTuple(tag_id=5, value_id=None),
                ),
                "prolong": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                    MeasurementToTags.TagStateTuple(tag_id=2, value_id=None)
                ),
                "end": ()
            }
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_new_tag_no_val_ends_same_tag_with_val(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ]
        }

        changes = self.msm_to_tags.calculate_changes(
            2,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            None,
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                ),
                "prolong": (),
                "end": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=1),
                )
            }
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_new_tag_no_val_ends_same_tag_with_val_mods_producer(
        self,
        tag_type
    ):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": [
                {
                    "tag_id": 1,
                    "value_id": None
                }
            ]
        }

        changes = self.msm_to_tags.calculate_changes(
            2,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "new_producer",
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                ),
                "prolong": (),
                "end": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=1),
                )
            }
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_check_new_tag_with_val_ends_same_tag_without_val(self, tag_type):
        taxonomy_db_info = {
            "taxonomy": {
                "id": 1
            },
            "tags": [
                {
                    "tag_id": 1,
                    "value_id": 2
                },
                {
                    "tag_id": 2,
                    "value_id": None
                }
            ]
        }

        changes = self.msm_to_tags.calculate_changes(
            1,  # tagged_id
            tag_type,
            parse_timestamp("2020-09-30T12:00:00"),  # measured_at
            "test_producer1",
            taxonomy_db_info
        )

        self.assertDictEqual(
            changes,
            {
                "insert": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=2),
                ),
                "prolong": (
                    MeasurementToTags.TagStateTuple(tag_id=2, value_id=None),
                ),
                "end": (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                )
            }
        )


class HandleMeasurementWriteChangesTest(PostgresPsycopgAdapterAutoDBTest):
    def setUp(self):
        super(HandleMeasurementWriteChangesTest, self).setUp()
        self.msm_to_tags = MeasurementToTags(self.adapter)

    def tearDown(self):
        super(HandleMeasurementWriteChangesTest, self).tearDown()

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_write_changes(self, intxn_type):
        intxn_mappings = INTXN_TABLE_MAPPINGS[intxn_type]

        self.msm_to_tags.write_intersection_changes(
            1,  # taxonomy_id
            parse_timestamp("2020-09-30T12:00:00"),  # timestamp
            {  # changes
                'insert': (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=2),
                ),
                'prolong': (
                    MeasurementToTags.TagStateTuple(tag_id=2, value_id=None),
                ),
                'end': (
                    MeasurementToTags.TagStateTuple(tag_id=1, value_id=None),
                )
            },
            intxn_type,
            1,  # tagged_id
            "test_producer_new"
        )
        self.adapter.commit()

        cursor = self.adapter.db_connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

        print(intxn_mappings)

        cursor.execute(
            """
            SELECT %(__fields__)s
            FROM %(table_name)s
            WHERE
                %(id)s = 1
                AND %(taxonomy_id)s = 1
            """ % intxn_mappings
        )
        rows = cursor.fetchall()
        self.assertIsNotNone(rows)
        for _row in rows:
            print("---")
            for key, val in _row.items():
                print("% 16s -> %s" % (str(key), str(val)))
        self.assertEqual(len(rows), 4)


class HandleMeasurementIntegrationTest(PostgresPsycopgAdapterAutoDBTest):
    def setUp(self):
        super(HandleMeasurementIntegrationTest, self).setUp()
        self.msm_to_tags = MeasurementToTags(self.adapter)

    def tearDown(self):
        super(HandleMeasurementIntegrationTest, self).tearDown()

    def is_tag_equal(a, b, type):
        if len(a) != len(b):
            _s = ""
            missing_a = set(b.keys()) - set(a.keys())
            if len(missing_a) > 0:
                _s += "missing_a:" + ",".join(missing_a)
            missing_b = set(a.keys()) - set(b.keys())
            if len(missing_b) > 0:
                _s += " missing_b:" + ",".join(missing_b)
            return False, _s

        for key, val in a.items():
            if key not in b:
                return False, "key:%s" % key
            if val != "{NEW}" and val != b[key]:
                return False, "key:%s:val:%s!=%s" % (key, val, b[key])
        return True, ""

    def is_tag_in_list(tag, list_, type):
        reasons = []
        for _list_tag in list_:
            _equ, _r = __class__.is_tag_equal(tag, _list_tag, type)
            if _equ:
                return True
            else:
                reasons.append(_r)
        print("this tag is not in the list:")
        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tag)
        print("offenders: %s" % (', '.join(reasons)))
        return False

    expected_tags = (
        MappingProxyType({  # 0
            'id': 1,
            'end_date': None,
            'end_ts': None,
            'measured_at': datetime.datetime(2020, 3, 17, 12, 53, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'start_date': 20200317,
            'start_ts': datetime.datetime(2020, 3, 17, 12, 53, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'tag_id': 1,
            'taxonomy_id': 1,
            'value_id': None,
            'producer': 'test_producer1'
        }),
        MappingProxyType({  # 1
            'id': 1,
            'end_date': None,
            'end_ts': None,
            'measured_at': datetime.datetime(2020, 6, 30, 20, 51, 36, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'start_date': 20200425,
            'start_ts': datetime.datetime(2020, 4, 25, 18, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'tag_id': 2,
            'taxonomy_id': 1,
            'value_id': None,
            'producer': 'test_producer1'
        }),
        MappingProxyType({  # 2
            'id': 1,
            'end_date': 20200710,
            'end_ts': datetime.datetime(2020, 7, 10, 14, 20, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'measured_at': datetime.datetime(2020, 7, 10, 14, 20, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'start_date': 20200425,
            'start_ts': datetime.datetime(2020, 4, 25, 18, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'tag_id': 3,
            'taxonomy_id': 1,
            'value_id': None,
            'producer': 'test_producer3'
        }),
        MappingProxyType({  # 3
            'id': 2,
            'end_date': None,
            'end_ts': None,
            'measured_at': datetime.datetime(2020, 3, 17, 12, 53, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'start_date': 20200317,
            'start_ts': datetime.datetime(2020, 3, 17, 12, 53, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
            'tag_id': 1,
            'taxonomy_id': 1,
            'value_id': 1,
            'producer': None
        }),
    )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_stale_measurement_fails(self, intxn_type):
        timestamp_str = "2010-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test",
            measured_at=timestamp_str,
            tags=[]
        )

        self.assertRaises(
            StaleMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    def test_unknown_tag_type_measurement_fails(self):
        timestamp_str = "2010-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type="some_other_tag_type",
            tagged_id=1,
            taxonomy=1,
            producer="test",
            measured_at=timestamp_str,
            tags=[]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_empty_taglist_by_id(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_producer1",
            measured_at=timestamp_text,
            tags=[]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = list(__class__.expected_tags)
        for i in [0, 1]:
            _new = dict(_expected[i])
            _new["measured_at"] = timestamp
            _new["end_ts"] = timestamp
            _new["end_date"] = int(timestamp.strftime("%Y%m%d"))
            _expected[i] = _new

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_empty_taglist_by_id_fail_on_diff_producer(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_other_producer",
            measured_at=timestamp_text,
            tags=[]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_empty_taglist_by_id_fail_on_none_producer(
        self,
        intxn_type
    ):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer=None,
            measured_at=timestamp_text,
            tags=[]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_prolong_tags(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_producer1",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1
                },
                {
                    "tag": 2
                }
            ]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = list(__class__.expected_tags)
        for i in [0, 1]:
            _new = dict(_expected[i])
            _new["measured_at"] = timestamp
            _expected[i] = _new

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    type=intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_prolong_tags_on_none_producer_sets_producer(
        self,
        intxn_type
    ):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=2,
            taxonomy=1,
            producer="new_test_producer",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1,
                    "value": 1
                }
            ]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        _expected = list(__class__.expected_tags)
        _new = dict(_expected[3])
        _new["measured_at"] = timestamp
        _new["producer"] = "new_test_producer"
        _expected[3] = _new

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)
        pprinter.pprint(_expected)

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    type=intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_prolong_tags_fail_on_different_producer(
        self,
        intxn_type
    ):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1
                },
                {
                    "tag": 2
                }
            ]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_prolong_tags_fail_on_none_producer(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer=None,
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1
                },
                {
                    "tag": 2
                }
            ]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_prolong_tags_2(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_producer1",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1
                },
                {
                    "tag": 2
                }
            ]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = list(__class__.expected_tags)
        for i in [0, 1]:
            _new = dict(_expected[i])
            _new["measured_at"] = timestamp
            _expected[i] = _new

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    type=intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_replace_tag_with_tag_with_value(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_producer1",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 1,
                    "value": 1
                },
                {
                    "tag": 2
                }
            ]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = list(__class__.expected_tags)

        _new = dict(_expected[0])
        _new["measured_at"] = timestamp
        _new["start_ts"] = timestamp
        _new["start_date"] = int(timestamp.strftime("%Y%m%d"))
        _new["value_id"] = 1

        _modified = dict(_expected[0])
        _modified["measured_at"] = timestamp
        _modified["end_ts"] = timestamp
        _modified["end_date"] = int(timestamp.strftime("%Y%m%d"))
        _expected[0] = _modified

        _modified = dict(_expected[1])
        _modified["measured_at"] = timestamp
        _expected[1] = _modified

        _expected.append(_new)

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_replace_tag_with_tag_with_value_by_name(
        self,
        intxn_type
    ):
        timestamp_text = "2020-10-01T09:00:00"
        timestamp = parse_timestamp(timestamp_text)
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=1,
            taxonomy=1,
            producer="test_producer1",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": "test_tag_1_tax_1",
                    "value": "value_1_tag_1"
                },
                {
                    "tag": "test_tag_2_tax_1"
                }
            ]
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(1, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = list(__class__.expected_tags)

        _new = dict(_expected[0])
        _new["start_ts"] = timestamp
        _new["start_date"] = int(timestamp.strftime("%Y%m%d"))
        _new["measured_at"] = timestamp
        _new["value_id"] = 1

        _modified = dict(_expected[0])
        _modified["measured_at"] = timestamp
        _modified["end_ts"] = timestamp
        _modified["end_date"] = int(timestamp.strftime("%Y%m%d"))
        _expected[0] = _modified

        _modified = dict(_expected[1])
        _modified["measured_at"] = timestamp
        _expected[1] = _modified

        _expected.append(_new)

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_add_tag_with_new_value(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=2,
            taxonomy="tax_test3",
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": "test_tag_1_tax_3",
                    "value": "some_new_value"
                }
            ],
            autogenerate_values=True
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(3, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = [
            {  # already existing tag
                'id': 1,
                'end_date': None,
                'end_ts': None,
                'measured_at': datetime.datetime(2020, 6, 30, 20, 51, 36, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'start_date': 20200425,
                'start_ts': datetime.datetime(2020, 4, 25, 18, 21, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'tag_id': 4,
                'taxonomy_id': 3,
                'value_id': None,
                'producer': 'test_producer3'
            },
            {  # new tag
                'id': 2,
                'end_date': None,
                'end_ts': None,
                'measured_at': datetime.datetime(2020, 10, 1, 9, 0, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'start_date': 20201001,
                'start_ts': datetime.datetime(2020, 10, 1, 9, 0, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'tag_id': 4,
                'taxonomy_id': 3,
                'value_id': '{NEW}',
                'producer': 'test'
            },
        ]

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    intxn_type
                )
            )

        values_for_tag = list(map(dict, self.adapter.get_tag_values(4)))

        _expected_values = [
            {
                'id': 3,
                'tag_id': 4,
                'value': 'value_1_tag_4'
            },
            {
                'id': '{NEW}',
                'tag_id': 4,
                'value': 'some_new_value'
            }
        ]

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(values_for_tag)

        self.assertEqual(len(_expected_values), len(values_for_tag))
        for _tag in _expected_values:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    values_for_tag,
                    intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_add_new_tag(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=3,
            taxonomy="tax_test2",
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": "some_new_tag",
                    "description": "some new awesome tag",
                    "extras": {
                        "test_extra": "xxx"
                    }
                }
            ],
            autogenerate_tags=True
        )

        self.msm_to_tags.handle_measurement(msm)

        tags_in_taxonomy = list(map(
            dict,
            self.adapter.get_taxonomy_intersections(2, intxn_type)
        ))

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags_in_taxonomy)

        _expected = [
            {
                'id': 3,
                'end_date': None,
                'end_ts': None,
                'measured_at': datetime.datetime(2020, 10, 1, 9, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'start_date': 20201001,
                'start_ts': datetime.datetime(2020, 10, 1, 9, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'tag_id': 5,
                'taxonomy_id': 2,
                'value_id': None,
                'producer': "test"
            },
        ]

        self.assertEqual(len(_expected), len(tags_in_taxonomy))

        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags_in_taxonomy,
                    intxn_type
                )
            )

        tags = list(map(dict, self.adapter.get_taxonomy_tags(2)))
        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(tags)

        _expected_tags = [
            {
                'extras': {'test_extra': 'xxx'},
                'tag_description': 'some new awesome tag',
                'tag_id': 5,
                'tag_name': 'some_new_tag',
                'taxonomy_id': 2
            },
        ]

        self.assertEqual(len(_expected_tags), len(tags))

        for _tag in _expected_tags:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    tags,
                    intxn_type
                )
            )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_add_tag_on_not_allowed_fails(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=3,
            taxonomy="tax_test2",
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": "some_new_tag",
                    "description": "some new awesome tag",
                    "extras": {
                        "test_extra": "xxx"
                    }
                }
            ]
        )

        self.assertRaises(
            InvalidMeasurementException,
            self.msm_to_tags.handle_measurement,
            msm
        )

        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=3,
            taxonomy="tax_test1",
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": "some_new_tag",
                    "description": "some new awesome tag",
                    "extras": {
                        "test_extra": "xxx"
                    }
                }
            ],
            autogenerate_tags=True
        )

        self.assertRaises(
            DisallowedTaxonomyModificationException,
            self.msm_to_tags.handle_measurement,
            msm
        )

    @parameterized.expand([("delegation",), ("domain", ), ("intersection", )])
    def test_measurement_add_value_with_space_twice_extends_tag(self, intxn_type):
        timestamp_text = "2020-10-01T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=2,
            taxonomy=3,
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 4,
                    "description": "some new awesome tag",
                    "value": " 5.1",
                    "extras": {
                        "test_extra": "xxx"
                    }
                }
            ],
            autogenerate_values=True
        )
        self.msm_to_tags.handle_measurement(msm)

        timestamp_text = "2020-10-16T09:00:00"
        msm = dict(
            version="1",
            tag_type=intxn_type,
            tagged_id=2,
            taxonomy=3,
            producer="test",
            measured_at=timestamp_text,
            tags=[
                {
                    "tag": 4,
                    "description": "some new awesome tag",
                    "value": " 5.1",
                    "extras": {
                        "test_extra": "xxx"
                    }
                }
            ],
            autogenerate_values=True
        )
        self.msm_to_tags.handle_measurement(msm)

        open_tags = self.adapter.get_all_tags(3, intxn_type, 2)

        _expected = [
            {  #
                'tag_id': 4,
                'value_id': '{NEW}',
                'start_ts': datetime.datetime(2020, 10, 1, 9, 0, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'measured_at': datetime.datetime(2020, 10, 16, 9, 0, 0, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'end_ts': None,
                'producer': 'test'
            }
        ]

        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(open_tags)

        self.assertEqual(len(_expected), len(open_tags))
        for _tag in _expected:
            self.assertTrue(
                __class__.is_tag_in_list(
                    _tag,
                    open_tags,
                    intxn_type
                )
            )
