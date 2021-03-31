from fastapi.testclient import TestClient

from tag2domain_api.app.main import app

from .db_test_classes import APIReadOnlyTest

client = TestClient(app)


class TestEndpointsTest(APIReadOnlyTest):
    def test_ping(self):
        response = client.get("/test/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "Pong!"}

    def test_self_test(self):
        response = client.get("/test/self-test")
        assert response.status_code == 200
        assert response.json() == {"message": "OK"}
