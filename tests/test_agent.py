from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_agent_executive():
    res = client.post(
        "/v1/ask-executive",
        json={"question": "why did revenue drop?"},
        headers={"X-API-Key": "test"}
    )
    assert res.status_code == 200
