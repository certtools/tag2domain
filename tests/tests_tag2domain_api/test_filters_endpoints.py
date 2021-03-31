from fastapi.testclient import TestClient

import pprint
from urllib.parse import urlencode

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)


class FiltersEndpointsTest(APIReadOnlyTest):
    def test_get_types(self):
        response = client.get("/api/v1/filters/types")
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == ["registrar-id", ]

    def test_get_values_type_exists(self):
        query = {"filter": "registrar-id"}
        response = client.get("/api/v1/filters/values/?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == ['1', '2', '3']

    def test_get_values_type_none_exist(self):
        query = {"filter": "some-other-filter"}
        response = client.get("/api/v1/filters/values/?%s" % urlencode(query))
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == []
