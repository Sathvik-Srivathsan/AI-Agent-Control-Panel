import uuid
from datetime import datetime, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.ai.agent import AgentRunResult, ToolCallRecord
from app.ai.client import LLMMessage
from app.db.models import Run, ToolCall
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


def test_run_persists_llm_requests():
    with patch("app.api.routes_runs.run_agent") as mock_run:
        mock_run.return_value = AgentRunResult(
            final_response="Done",
            status="success",
            tool_calls=[],
            llm_requests=2,
        )
        response = client.post("/agents/code-assistant/run", json={"prompt": "test"})
        run_id = response.json()["run_id"]
        detail = client.get(f"/runs/{run_id}").json()
        assert detail["llm_requests"] == 2


def test_run_persists_transcript_messages():
    with patch("app.api.routes_runs.run_agent") as mock_run:
        mock_run.return_value = AgentRunResult(
            final_response="Final answer",
            status="success",
            tool_calls=[
                ToolCallRecord(
                    tool_name="list_files",
                    arguments='{"path": ""}',
                    result="f main.py",
                    status="success",
                    duration_ms=10,
                ),
            ],
            llm_requests=2,
            messages=[
                LLMMessage(role="assistant", content="", tool_calls=[{"id": "c1", "function": {"name": "list_files", "arguments": '{"path": ""}'}}]),
                LLMMessage(role="tool", content="f main.py", tool_call_id="c1"),
            ],
        )
        response = client.post("/agents/code-assistant/run", json={"prompt": "list files"})
        run_id = response.json()["run_id"]
        messages = client.get(f"/runs/{run_id}/messages").json()
        roles = [m["role"] for m in messages]
        assert roles == ["user", "assistant", "tool", "assistant"]
        assert messages[2]["content"] == "f main.py"
        assert messages[3]["content"] == "Final answer"


def test_get_run_messages_404():
    response = client.get("/runs/nonexistent/messages")
    assert response.status_code == 404


def test_get_metrics_empty():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_runs"] == 0
    assert data["success_rate"] == 0.0
    assert data["avg_tool_calls_per_run"] == 0.0


def test_get_metrics_with_runs():
    db = TestSession()
    db.add_all(
        [
            Run(
                id=str(uuid.uuid4()),
                agent_id="code-assistant",
                prompt="a",
                final_response="ok",
                status="success",
                model="test-model",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                duration_ms=200,
                llm_requests=2,
            ),
            Run(
                id=str(uuid.uuid4()),
                agent_id="code-assistant",
                prompt="b",
                status="error",
                model="test-model",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                duration_ms=400,
                llm_requests=1,
                error="boom",
            ),
        ]
    )
    db.commit()
    run = db.query(Run).filter(Run.prompt == "a").first()
    db.add(
        ToolCall(
            id=str(uuid.uuid4()),
            run_id=run.id,
            tool_name="read_file",
            arguments="{}",
            result="content",
            status="success",
            duration_ms=50,
        )
    )
    db.commit()
    db.close()

    data = client.get("/metrics").json()
    assert data["total_runs"] == 2
    assert data["successful_runs"] == 1
    assert data["failed_runs"] == 1
    assert data["success_rate"] == 50.0
    assert data["avg_duration_ms"] == 300.0
    assert data["avg_llm_requests"] == 1.5
    assert data["total_tool_calls"] == 1
    assert data["error_tool_calls"] == 0
    assert data["avg_tool_calls_per_run"] == 0.5
    assert data["agents"] == 1
    assert data["last_run_at"] is not None
