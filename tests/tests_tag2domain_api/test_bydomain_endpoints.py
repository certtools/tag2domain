from fastapi.testclient import TestClient

import pprint

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)


class ByDomainEndpointsTest(APIReadOnlyTest):
    def test_bydomain_open_tags(self):
        response = client.get("/api/v1/bydomain/test1.at")
        assert response.status_code == 200
        assert response.json() == DOMAIN_TEST1_OPEN_TAGS

    def test_bydomain_tags_history(self):
        response = client.get("/api/v1/bydomain/test1.at/history")
        assert response.status_code == 200
        assert response.json() == DOMAIN_TEST1_TAG_HISTORY

    def test_bydomain_tags_nonexisting(self):
        response = client.get("/api/v1/bydomain/test_nonexisting.at")
        assert response.status_code == 200
        assert response.json() == []

    def test_bydomain_tags_history_nonexisting(self):
        response = client.get("/api/v1/bydomain/test_nonexisting.at/history")
        assert response.status_code == 200
        assert response.json() == []


DOMAIN_TEST1_OPEN_TAGS = list(sorted([
    {
        'end_time': None,
        'measured_at': '2020-03-17T12:53:21+00:00',
        'start_time': '2020-03-17T12:53:21+00:00',
        'tag_id': 1,
        'tag_name': 'test_tag_1_tax_1',
        'taxonomy_id': 1,
        'taxonomy_name': 'tax_test1',
        'value': None,
        'value_id': None
    },
    {
        'end_time': None,
        'measured_at': '2020-06-30T20:51:36+00:00',
        'start_time': '2020-04-25T18:21:00+00:00',
        'tag_id': 2,
        'tag_name': 'test_tag_2_tax_1',
        'taxonomy_id': 1,
        'taxonomy_name': 'tax_test1',
        'value': None,
        'value_id': None
    },
    {
        'end_time': None,
        'measured_at': '2020-06-30T20:51:36+00:00',
        'start_time': '2020-04-25T18:21:00+00:00',
        'tag_id': 4,
        'tag_name': 'test_tag_1_tax_3',
        'taxonomy_id': 3,
        'taxonomy_name': 'tax_test3',
        'value': None,
        'value_id': None
    },
] * 3, key=lambda tag: tag["tag_id"]))

DOMAIN_TEST1_TAG_HISTORY = list(sorted([
    {
        'end_time': None,
        'measured_at': '2020-03-17T12:53:21+00:00',
        'start_time': '2020-03-17T12:53:21+00:00',
        'tag_id': 1,
        'tag_name': 'test_tag_1_tax_1',
        'taxonomy_id': 1,
        'taxonomy_name': 'tax_test1',
        'value': None,
        'value_id': None
    },
    {
        'end_time': None,
        'measured_at': '2020-06-30T20:51:36+00:00',
        'start_time': '2020-04-25T18:21:00+00:00',
        'tag_id': 2,
        'tag_name': 'test_tag_2_tax_1',
        'taxonomy_id': 1,
        'taxonomy_name': 'tax_test1',
        'value': None,
        'value_id': None
    },
    {
        'end_time': None,
        'measured_at': '2020-06-30T20:51:36+00:00',
        'start_time': '2020-04-25T18:21:00+00:00',
        'tag_id': 4,
        'tag_name': 'test_tag_1_tax_3',
        'taxonomy_id': 3,
        'taxonomy_name': 'tax_test3',
        'value': None,
        'value_id': None
    },
    {
        'end_time': '2020-07-10T14:20:00+00:00',
        'measured_at': '2020-07-10T14:20:00+00:00',
        'start_time': '2020-04-25T18:21:00+00:00',
        'tag_id': 3,
        'tag_name': 'test_tag_3_tax_1',
        'taxonomy_id': 1,
        'taxonomy_name': 'tax_test1',
        'value': None,
        'value_id': None
    }
] * 3, key=lambda tag: tag["tag_id"]))
