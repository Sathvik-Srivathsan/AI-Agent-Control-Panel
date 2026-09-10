from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.ai.agent import AgentRunResult, ToolCallRecord
from tests.conftest import TestSession

client = TestClient(app)


def test_run_agent_returns_200():
    with patch("app.api.routes_runs.run_agent") as mock_run:
        mock_run.return_value = AgentRunResult(
            final_response="Analysis complete",
            status="success",
            tool_calls=[],
            llm_requests=1,
        )
        response = client.post("/agents/code-assistant/run", json={"prompt": "analyze main.py"})
        assert response.status_code == 200


def test_run_agent_returns_correct_structure():
    with patch("app.api.routes_runs.run_agent") as mock_run:
        mock_run.return_value = AgentRunResult(
            final_response="Found issues",
            status="success",
            tool_calls=[],
            llm_requests=1,
        )
        response = client.post("/agents/code-assistant/run", json={"prompt": "check code"})
        data = response.json()
        assert data["agent"] == "Code Assistant"
        assert data["status"] == "success"
        assert data["response"] == "Found issues"
        assert "run_id" in data
        assert "duration_ms" in data


def test_run_agent_not_found_returns_404():
    response = client.post("/agents/nonexistent/run", json={"prompt": "test"})
    assert response.status_code == 404


def test_run_agent_disabled_returns_400():
    db = TestSession()
    from app.db.models import Agent
    agent = db.query(Agent).filter(Agent.id == "code-assistant").first()
    agent.enabled = False
    db.commit()
    db.close()

    response = client.post("/agents/code-assistant/run", json={"prompt": "test"})
    assert response.status_code == 400


def test_run_agent_missing_prompt_returns_422():
    response = client.post("/agents/code-assistant/run", json={})
    assert response.status_code == 422


def test_run_agent_with_tool_calls():
    with patch("app.api.routes_runs.run_agent") as mock_run:
        mock_run.return_value = AgentRunResult(
            final_response="Here are the files",
            status="success",
            tool_calls=[
                ToolCallRecord(
                    tool_name="list_files",
                    arguments='{"path": ""}',
                    result="f main.py",
                    status="success",
                    duration_ms=50,
                ),
            ],
            llm_requests=2,
        )
        response = client.post("/agents/code-assistant/run", json={"prompt": "list files"})
        data = response.json()
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool"] == "list_files"
