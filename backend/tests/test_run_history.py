import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Run, ToolCall
from tests.conftest import TestSession

client = TestClient(app)


def _create_run(prompt="test prompt", status="success", tool_count=0):
    db = TestSession()
    run_id = str(uuid.uuid4())
    run = Run(
        id=run_id,
        agent_id="code-assistant",
        prompt=prompt,
        final_response="test response",
        status=status,
        model="test-model",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_ms=1000,
    )
    db.add(run)
    for i in range(tool_count):
        db.add(
            ToolCall(
                id=str(uuid.uuid4()),
                run_id=run_id,
                tool_name="list_files",
                arguments='{"path": ""}',
                result="f main.py",
                status="success",
                duration_ms=50,
            )
        )
    db.commit()
    db.close()
    return run_id


def test_list_runs_returns_200():
    response = client.get("/runs")
    assert response.status_code == 200


def test_list_runs_returns_list():
    response = client.get("/runs")
    data = response.json()
    assert isinstance(data, list)


def test_list_runs_contains_created_run():
    run_id = _create_run()
    response = client.get("/runs")
    data = response.json()
    ids = [r["id"] for r in data]
    assert run_id in ids


def test_get_run_returns_200():
    run_id = _create_run()
    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200


def test_get_run_returns_correct_data():
    run_id = _create_run(prompt="analyze bugs")
    response = client.get(f"/runs/{run_id}")
    data = response.json()
    assert data["id"] == run_id
    assert data["prompt"] == "analyze bugs"
    assert data["status"] == "success"
    assert data["final_response"] == "test response"


def test_get_run_not_found_returns_404():
    response = client.get("/runs/nonexistent")
    assert response.status_code == 404


def test_get_run_tools_returns_200():
    run_id = _create_run(tool_count=2)
    response = client.get(f"/runs/{run_id}/tools")
    assert response.status_code == 200


def test_get_run_tools_returns_list():
    run_id = _create_run(tool_count=3)
    response = client.get(f"/runs/{run_id}/tools")
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_get_run_tools_returns_correct_data():
    run_id = _create_run(tool_count=1)
    response = client.get(f"/runs/{run_id}/tools")
    data = response.json()
    assert data[0]["tool_name"] == "list_files"
    assert data[0]["status"] == "success"


def test_get_run_tools_not_found_returns_404():
    response = client.get("/runs/nonexistent/tools")
    assert response.status_code == 404


def test_list_runs_ordered_by_started_at():
    id1 = _create_run(prompt="first")
    id2 = _create_run(prompt="second")
    response = client.get("/runs")
    data = response.json()
    prompts = [r["prompt"] for r in data]
    assert prompts.index("second") < prompts.index("first")
