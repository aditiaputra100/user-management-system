from fastapi.testclient import TestClient

def test_main(client: TestClient):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"msg": "OK"}