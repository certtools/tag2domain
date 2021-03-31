from fastapi.testclient import TestClient

import pprint
from parameterized import parameterized
from urllib.parse import urlencode

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest, APIWithAdditionalDBDataTest

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)

BYTAG_CASES = [

    (  # query tag that is not in DB
        {"tag": "some_unknown_open_tag"},
        []
    ),
    (  # tag that exists but query before it was opened
        {
            "tag": "test_tag_1_tax_1",
            "at_time": "2010-01-01T12:00:00"
        },
        []
    ),
    (  # query existing open tag
        {"tag": "test_tag_1_tax_1"},
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'delegation',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'domain',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'intersection',
                'value': None
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'delegation',
                'value': 'value_1_tag_1'
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'domain',
                'value': 'value_1_tag_1'
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'intersection',
                'value': 'value_1_tag_1'
            }
        ]
    ),
    (  # query existing open tags - limit 2, offset 1
        {
            "tag": "test_tag_1_tax_1",
            "limit": 2,
            "offset": 1
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'domain',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'intersection',
                'value': None
            }
        ]
    ),
    (  # query existing tag at time in the past
        {
            "tag": "test_tag_3_tax_1",
            "at_time": "2020-06-01T12:00:00"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'delegation',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'domain',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'intersection',
                'value': None
            }
        ]
    ),
    (  # query the same tag as the one in the previous case but at a time where
       # it is not active
        {
            "tag": "test_tag_3_tax_1",
            "at_time": "2020-08-01T12:00:00"
        },
        []
    ),
    (  # query the same tag as the one in the previous case but query open tags
        {
            "tag": "test_tag_3_tax_1"
        },
        []
    ),
    (  # query existing open tag with filter
        {
            "tag": "test_tag_1_tax_1",
            "filter": "registrar-id=1"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'intersection',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'domain',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': None,
                'measured_at': '2020-03-17T12:53:21+00:00',
                'start_time': '2020-03-17T12:53:21+00:00',
                'tag_type': 'delegation',
                'value': None
            }
        ]
    ),
    (  # query with at_time and a filter
        {
            "tag": "test_tag_3_tax_1",
            "at_time": "2020-06-01T12:00:00",
            "filter": "registrar-id=1"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'delegation',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'domain',
                'value': None
            },
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'end_time': '2020-07-10T14:20:00+00:00',
                'measured_at': '2020-07-10T14:20:00+00:00',
                'start_time': '2020-04-25T18:21:00+00:00',
                'tag_type': 'intersection',
                'value': None
            }
        ]
    ),
    (  # query with at_time and a filter that matches nothing
        {
            "tag": "test_tag_3_tax_1",
            "at_time": "2020-06-01T12:00:00",
            "filter": "registrar-id=2"
        },
        []
    ),
]

BYTAXONOMY_CASES = [
    (  # all domains with open tags in taxonomy tax_test1
        {
            "taxonomy": "tax_test1"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    }
                ]
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    }
                ]
            }
        ]
    ),
    (  # all domains on date where no tags exists (result empty)
        {
            "taxonomy": "tax_test1",
            "at_time": "2010-01-01T12:00:00"
        },
        []
    ),
    (  # all domains with tags on past date
        {
            "taxonomy": "tax_test1",
            "at_time": "2020-06-01T12:00:00"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-06-30T20:51:36+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 2,
                        'tag_name': 'test_tag_2_tax_1'
                    },
                    {
                        'end_time': '2020-07-10T14:20:00+00:00',
                        'measured_at': '2020-07-10T14:20:00+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 3,
                        'tag_name': 'test_tag_3_tax_1'
                    },
                    {
                        'end_time': '2020-07-10T14:20:00+00:00',
                        'measured_at': '2020-07-10T14:20:00+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 3,
                        'tag_name': 'test_tag_3_tax_1'
                    },
                    {
                        'end_time': '2020-07-10T14:20:00+00:00',
                        'measured_at': '2020-07-10T14:20:00+00:00',
                        'start_time': '2020-04-25T18:21:00+00:00',
                        'tag_id': 3,
                        'tag_name': 'test_tag_3_tax_1'
                    }
                ]
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'},
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'},
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 1,
                        'tag_name': 'test_tag_1_tax_1'
                    }
                ]
            }
        ]
    )
]


class DomainsEndpointsTest(APIReadOnlyTest):
    @parameterized.expand(BYTAG_CASES)
    def test_bytag(self, query, result):
        response = client.get("/api/v1/domains/bytag?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == result

    @parameterized.expand(BYTAXONOMY_CASES)
    def test_bytaxonomy(self, query, result):
        response = client.get(
            "/api/v1/domains/bytaxonomy?%s" % urlencode(query)
        )
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == result


BYVERSION_CASES = [
    (  # version equal
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "1.0.2",
            "operator": "="
        },
        [{'domain_id': 1, 'domain_name': 'test1.at', 'version': '1.0.2', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None}]
    ),
    (  # version less than major
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "2",
            "operator": "<"
        },
        [{'domain_id': 1, 'domain_name': 'test1.at', 'version': '1.0.2', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None}]
    ),
    (  # version greater than major
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "2",
            "operator": ">"
        },
        [{'domain_id': 2, 'domain_name': 'test2.at', 'version': '2.1.0', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None}]
    ),
    (  # version greater than major both
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "1",
            "operator": ">"
        },
        [
            {'domain_id': 1, 'domain_name': 'test1.at', 'version': '1.0.2', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None},
            {'domain_id': 2, 'domain_name': 'test2.at', 'version': '2.1.0', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None}
        ]
    ),
    (  # version greater than major both time in the past
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "1",
            "operator": ">",
            "at_time": "2020-06-01T12:00:00"
        },
        [
            {'domain_id': 1, 'domain_name': 'test1.at', 'version': '1.0.2', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None},
            {'domain_id': 2, 'domain_name': 'test2.at', 'version': '2.1.0', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-03-17T12:53:21+00:00', 'end_time': None},
            {'domain_id': 3, 'domain_name': 'test3.at', 'version': '2.1.0', 'start_time': '2020-03-17T12:53:21+00:00', 'measured_at': '2020-08-20T12:53:21+00:00', 'end_time': '2020-08-20T12:53:21+00:00'}
        ]
    ),
    (  # version greater than major both time way in the past
        {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1",
            "version": "1",
            "operator": ">",
            "at_time": "2010-06-01T12:00:00"
        },
        []
    )
]


class DomainsByVersionsTest(APIWithAdditionalDBDataTest):
    def setUp(self):
        super(DomainsByVersionsTest, self).setUp("version_tags")

    @parameterized.expand(BYVERSION_CASES)
    def test_version_equal(self, query, result):
        response = client.get("/api/v1/domains/byversion?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == result


BYCATEGORY_CASES = [
    (  # fetch empty category
        {
            "taxonomy": "tax_test4"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 2000564,
                        'tag_name': 'test_tag_4_tax_4'
                    }
                ]
            }
        ]
    ),
    (  # cat_1 -> 2 tags / 1 domain
        {
            "taxonomy": "tax_test4",
            "category": "cat_1"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 2000561,
                        'tag_name': 'cat_1::test_tag_1_tax_4'
                    },
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 2000562,
                        'tag_name': 'cat_1::test_tag_2_tax_4'
                    }
                ]
            }
        ]
    ),
    (  # cat_2 -> 1 tag / 2 domains
        {
            "taxonomy": "tax_test4",
            "category": "cat_2"
        },
        [
            {
                'domain_id': 1,
                'domain_name': 'test1.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 2000563,
                        'tag_name': 'cat_2::test_tag_3_tax_4'
                    }
                ]
            },
            {
                'domain_id': 2,
                'domain_name': 'test2.at',
                'tags': [
                    {
                        'end_time': None,
                        'measured_at': '2020-03-17T12:53:21+00:00',
                        'start_time': '2020-03-17T12:53:21+00:00',
                        'tag_id': 2000563,
                        'tag_name': 'cat_2::test_tag_3_tax_4'
                    }
                ]
            }
        ]
    ),
]


class DomainsByCategoriesTest(APIWithAdditionalDBDataTest):
    def setUp(self):
        super(DomainsByCategoriesTest, self).setUp("tags_categories")

    @parameterized.expand(BYCATEGORY_CASES)
    def test_get_domains_by_category(self, query, result):
        response = client.get("/api/v1/domains/bycategory?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == result
