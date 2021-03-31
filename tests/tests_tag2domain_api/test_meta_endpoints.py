from fastapi.testclient import TestClient

import pprint
from urllib.parse import urlencode

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest, APIWithAdditionalDBDataTest

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)


class MetaEndpointsTest(APIReadOnlyTest):
    def test_get_taxonomies(self):
        response = client.get("/api/v1/meta/taxonomies")
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {
                'description': 'test taxonomie 1',
                'for_domains': True,
                'for_numbers': True,
                'id': 1,
                'is_actionable': 1.0,
                'is_automatically_classifiable': 1.0,
                'is_stable': 0.0,
                'name': 'tax_test1',
                'url': 'test.at/test_taxonomie_1'},
            {
                'description': 'test taxonomie 2',
                'for_domains': True,
                'for_numbers': True,
                'id': 2,
                'is_actionable': 1.0,
                'is_automatically_classifiable': 1.0,
                'is_stable': 0.0,
                'name': 'tax_test2',
                'url': 'test.at/test_taxonomie_2'},
            {
                'description': 'test taxonomie 3',
                'for_domains': True,
                'for_numbers': True,
                'id': 3,
                'is_actionable': 0.5,
                'is_automatically_classifiable': 1.0,
                'is_stable': 0.0,
                'name': 'tax_test3',
                'url': 'test.at/test_taxonomie_3'},
            {
                'description': 'test taxonomie 4',
                'for_domains': True,
                'for_numbers': True,
                'id': 4,
                'is_actionable': None,
                'is_automatically_classifiable': 1.0,
                'is_stable': 0.0,
                'name': 'tax_test4',
                'url': 'test.at/test_taxonomie_4'
            }
        ]

    def test_get_tags_all(self):
        response = client.get("/api/v1/meta/tags")
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {
                'extras': {},
                'tag_description': 'test tag 1 for tax 1',
                'tag_id': 1,
                'tag_name': 'test_tag_1_tax_1',
                'taxonomy_id': 1
            },
            {
                'extras': {},
                'tag_description': 'test tag 2 for tax 1',
                'tag_id': 2,
                'tag_name': 'test_tag_2_tax_1',
                'taxonomy_id': 1
            },
            {
                'extras': {},
                'tag_description': 'test tag 3 for tax 1',
                'tag_id': 3,
                'tag_name': 'test_tag_3_tax_1',
                'taxonomy_id': 1
            },
            {
                'extras': {},
                'tag_description': 'test tag 1 for tax 3',
                'tag_id': 4,
                'tag_name': 'test_tag_1_tax_3',
                'taxonomy_id': 3
            }
        ]

    def test_get_values_existing(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1"
        }
        response = client.get("/api/v1/meta/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {'value': 'value_1_tag_1', 'value_id': 1},
            {'value': 'value_2_tag_1', 'value_id': 2}
        ]

    def test_get_values_non_existing(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_2_tax_1"
        }
        response = client.get("/api/v1/meta/values?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tag_info_existing(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_1_tax_1"
        }
        response = client.get("/api/v1/meta/tag?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == {
            'tag': {
                'category': None,
                'description': 'test tag 1 for tax 1',
                'extras': {},
                'name': 'test_tag_1_tax_1'
            },
            'taxonomy': {
                'description': 'test taxonomie 1',
                'flags': {
                    'allows_auto_tags': False,
                    'allows_auto_values': False,
                    'for_domains': True,
                    'for_numbers': True,
                    'is_actionable': 1.0,
                    'is_automatically_classifiable': True,
                    'is_stable': True},
                'name': 'tax_test1',
                'url': 'test.at/test_taxonomie_1'
            },
            'values': {'count': 2}
        }

    def test_get_tag_info_non_existing(self):
        query = {
            "taxonomy": "tax_test1",
            "tag": "test_tag_non_existing"
        }
        response = client.get("/api/v1/meta/tag?%s" % urlencode(query))
        assert response.status_code == 404


class MetaEndpointsWithCategoriesTest(APIWithAdditionalDBDataTest):
    def setUp(self):
        super(MetaEndpointsWithCategoriesTest, self).setUp("tags_categories")

    def test_get_categories_no_cats_exist(self):
        query = {
            "taxonomy": "tax_test1"
        }
        response = client.get("/api/v1/meta/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [""]

    def test_get_categories_cats_exist(self):
        query = {
            "taxonomy": "tax_test4"
        }
        response = client.get("/api/v1/meta/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert set(response.json()) == set([
            "",
            "cat_1",
            "cat_2"
        ])

    def test_get_all_categories(self):
        query = {}
        response = client.get("/api/v1/meta/categories?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert set(response.json()) == set([
            "",
            "cat_1",
            "cat_2"
        ])

    def test_get_tags_cat_1(self):
        query = {
            "taxonomy": "tax_test4",
            "category": "cat_1"
        }
        response = client.get("/api/v1/meta/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {
                'extras': {},
                'tag_description': 'test tag 1 for tax 4 (cat 1)',
                'tag_id': 2000561,
                'tag_name': 'cat_1::test_tag_1_tax_4',
                'taxonomy_id': 4
            },
            {
                'extras': {},
                'tag_description': 'test tag 2 for tax 4 (cat 1)',
                'tag_id': 2000562,
                'tag_name': 'cat_1::test_tag_2_tax_4',
                'taxonomy_id': 4
            }
        ]

    def test_get_tags_no_cat(self):
        query = {
            "taxonomy": "tax_test4",
            "category": ""
        }
        response = client.get("/api/v1/meta/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {
                'extras': {},
                'tag_description': 'test tag 4 for tax 4 (no cat)',
                'tag_id': 2000564,
                'tag_name': 'test_tag_4_tax_4',
                'taxonomy_id': 4
            }
        ]

    def test_get_tags_all_tax_test_4(self):
        query = {
            "taxonomy": "tax_test4"
        }
        response = client.get("/api/v1/meta/tags?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == [
            {
                'extras': {},
                'tag_description': 'test tag 1 for tax 4 (cat 1)',
                'tag_id': 2000561,
                'tag_name': 'cat_1::test_tag_1_tax_4',
                'taxonomy_id': 4
            },
            {
                'extras': {},
                'tag_description': 'test tag 2 for tax 4 (cat 1)',
                'tag_id': 2000562,
                'tag_name': 'cat_1::test_tag_2_tax_4',
                'taxonomy_id': 4
            },
            {
                'tag_id': 2000563,
                'tag_name': 'cat_2::test_tag_3_tax_4',
                'tag_description': 'test tag 3 for tax 4 (cat 2)',
                'taxonomy_id': 4,
                'extras': {}
            },
            {
                'extras': {},
                'tag_description': 'test tag 4 for tax 4 (no cat)',
                'tag_id': 2000564,
                'tag_name': 'test_tag_4_tax_4',
                'taxonomy_id': 4
            }
        ]

    def test_get_tags_fail_missing_taxonomy(self):
        query = {
            "category": "cat_1"
        }
        response = client.get("/api/v1/meta/tags?%s" % urlencode(query))
        assert response.status_code == 400
