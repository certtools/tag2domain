from fastapi.testclient import TestClient

import pprint
from urllib.parse import urlencode

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest, APIWithAdditionalDBDataTest

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)


class StatsEndpointTaxonomiesTest(APIReadOnlyTest):
    def test_taxonomy_stats_all(self):
        response = client.get("/api/v1/stats/taxonomies")
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 2, 'taxonomy_name': 'tax_test1'},
            {'count': 1, 'taxonomy_name': 'tax_test3'}
        ]

    def test_taxonomy_stats_past(self):
        query = {
            'at_time': '2020-10-01T12:00:00'
        }
        response = client.get("/api/v1/stats/taxonomies?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 2, 'taxonomy_name': 'tax_test1'},
            {'count': 1, 'taxonomy_name': 'tax_test3'}
        ]

    def test_taxonomy_stats_distant_past(self):
        query = {
            'at_time': '2010-10-01T12:00:00'
        }
        response = client.get("/api/v1/stats/taxonomies?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_taxonomy_stats_filter(self):
        query = {
            'filter': 'registrar-id=1'
        }
        response = client.get("/api/v1/stats/taxonomies?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 1, 'taxonomy_name': 'tax_test1'},
            {'count': 1, 'taxonomy_name': 'tax_test3'}
        ]

    def test_taxonomy_stats_filter_past(self):
        query = {
            'at_time': '2020-10-01T12:00:00',
            'filter': 'registrar-id=1'
        }
        response = client.get("/api/v1/stats/taxonomies?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 1, 'taxonomy_name': 'tax_test1'},
            {'count': 1, 'taxonomy_name': 'tax_test3'}
        ]


class StatsEndpointCategoriesTest(APIWithAdditionalDBDataTest):
    def setUp(self):
        super(StatsEndpointCategoriesTest, self).setUp("tags_categories")

    def test_category_stats_all(self):
        query = {"taxonomy": "tax_test4"}
        response = client.get("/api/v1/stats/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'category': 'cat_2', 'count': 2},
            {'category': '', 'count': 1},
            {'category': 'cat_1', 'count': 1}
        ]

    def test_category_stats_past(self):
        query = {
            "taxonomy": "tax_test4",
            "at_time": "2020-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'category': 'cat_2', 'count': 2},
            {'category': '', 'count': 1},
            {'category': 'cat_1', 'count': 1}
        ]

    def test_category_stats_distant_past(self):
        query = {
            "taxonomy": "tax_test4",
            "at_time": "2010-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_category_stats_filter(self):
        query = {
            "taxonomy": "tax_test4",
            "filter": "registrar-id=1"
        }
        response = client.get("/api/v1/stats/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'category': 'cat_2', 'count': 1},
            {'category': '', 'count': 1},
            {'category': 'cat_1', 'count': 1}
        ]


class StatsEndpointTagsTest(APIWithAdditionalDBDataTest):
    def setUp(self):
        super(StatsEndpointTagsTest, self).setUp("tags_categories")

    def test_tag_stats_tax_test1_all(self):
        query = {
            "taxonomy": "tax_test1"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 2, 'tag_name': 'test_tag_1_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_2_tax_1'}
        ]

    def test_tag_stats_tax_test1_past(self):
        query = {
            "taxonomy": "tax_test1",
            "at_time": "2020-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 2, 'tag_name': 'test_tag_1_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_2_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_3_tax_1'}
        ]

    def test_tag_stats_tax_test1_distant_past(self):
        query = {
            "taxonomy": "tax_test1",
            "at_time": "2010-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_tag_stats_tax_test1_filter(self):
        query = {
            "taxonomy": "tax_test1",
            "filter": "registrar-id=1"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 1, 'tag_name': 'test_tag_1_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_2_tax_1'}
        ]

    def test_tag_stats_tax_test1_past_filter(self):
        query = {
            "taxonomy": "tax_test1",
            "at_time": "2020-06-01T12:00:00",
            "filter": "registrar-id=1"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 2, 'tag_name': 'test_tag_1_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_2_tax_1'},
            {'count': 1, 'tag_name': 'test_tag_3_tax_1'}
        ]

    def test_tag_stats_cat_1(self):
        query = {
            "taxonomy": "tax_test4",
            "category": "cat_1"
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 1, 'tag_name': 'cat_1::test_tag_1_tax_4'},
            {'count': 1, 'tag_name': 'cat_1::test_tag_2_tax_4'}
        ]

    def test_tag_stats_no_cat(self):
        query = {
            "taxonomy": "tax_test4",
            "category": ""
        }
        response = client.get("/api/v1/stats/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'count': 1, 'tag_name': 'test_tag_4_tax_4'}
        ]


class StatsEndpointValuesTest(APIReadOnlyTest):
    def test_value_stats__tag_1_tax_1(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [{'count': 1, 'value': 'value_1_tag_1'}]

    def test_value_stats__tag_1_tax_1_past(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1",
            "at_time": "2020-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [{'count': 1, 'value': 'value_1_tag_1'}]

    def test_value_stats__tag_1_tax_1_distant_past(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1",
            "at_time": "2010-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_value_stats__tag_1_tax_1_filter(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1",
            "filter": "registrar-id=1"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_value_stats__tag_1_tax_1_filter_past(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1",
            "filter": "registrar-id=1",
            "at_time": "2020-06-01T12:00:00"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [{'count': 1, 'value': 'value_1_tag_1'}]

    def test_value_stats__tag_1_tax_1_filter2(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1",
            "filter": "registrar-id=2"
        }
        response = client.get("/api/v1/stats/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []
