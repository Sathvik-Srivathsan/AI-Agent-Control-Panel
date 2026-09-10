from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_agents_returns_200():
    response = client.get("/agents")
    assert response.status_code == 200


def test_list_agents_returns_list():
    response = client.get("/agents")
    data = response.json()
    assert isinstance(data, list)


def test_list_agents_contains_code_assistant():
    response = client.get("/agents")
    data = response.json()
    ids = [a["id"] for a in data]
    assert "code-assistant" in ids


def test_get_agent_returns_200():
    response = client.get("/agents/code-assistant")
    assert response.status_code == 200


def test_get_agent_returns_correct_data():
    response = client.get("/agents/code-assistant")
    data = response.json()
    assert data["id"] == "code-assistant"
    assert data["name"] == "Code Assistant"
    assert "system_prompt" in data


def test_get_agent_not_found_returns_404():
    response = client.get("/agents/nonexistent")
    assert response.status_code == 404


def test_get_agent_not_found_returns_detail():
    response = client.get("/agents/nonexistent")
    data = response.json()
    assert "detail" in data
