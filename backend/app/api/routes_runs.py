from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import time
from datetime import datetime, timezone

from app.db.database import get_db
from app.db.models import Agent, Run, ToolCall, Message
from app.ai.client import LLMClient
from app.ai.agent import run_agent
from app.tools import filesystem  # noqa: F401 - registers tools on import
from app.schemas.runs import RunRequest, RunResponse, ToolCallResponse

router = APIRouter()


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.started_at.desc()).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "prompt": r.prompt,
            "status": r.status,
            "model": r.model,
            "duration_ms": r.duration_ms,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return {
        "id": run.id,
        "agent_id": run.agent_id,
        "prompt": run.prompt,
        "final_response": run.final_response,
        "status": run.status,
        "model": run.model,
        "duration_ms": run.duration_ms,
        "error": run.error,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


@router.get("/runs/{run_id}/tools")
def get_run_tools(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    tool_calls = db.query(ToolCall).filter(ToolCall.run_id == run_id).all()
    return [
        {
            "id": tc.id,
            "tool_name": tc.tool_name,
            "arguments": tc.arguments,
            "result": tc.result,
            "status": tc.status,
            "duration_ms": tc.duration_ms,
        }
        for tc in tool_calls
    ]


@router.post("/agents/{agent_id}/run", response_model=RunResponse)
def run_agent_endpoint(agent_id: str, req: RunRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if not agent.enabled:
        raise HTTPException(status_code=400, detail=f"Agent '{agent_id}' is disabled")

    run_id = str(uuid.uuid4())
    start_time = time.time()

    run = Run(
        id=run_id,
        agent_id=agent_id,
        prompt=req.prompt,
        status="running",
        model=agent.model,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()

    db.add(Message(id=str(uuid.uuid4()), run_id=run_id, role="user", content=req.prompt))
    db.commit()

    llm_client = LLMClient()
    result = run_agent(agent, req.prompt, llm_client)

    duration_ms = int((time.time() - start_time) * 1000)

    run.status = result.status
    run.final_response = result.final_response
    run.completed_at = datetime.now(timezone.utc)
    run.duration_ms = duration_ms
    if result.error:
        run.error = result.error
    db.commit()

    for tc in result.tool_calls:
        db.add(
            ToolCall(
                id=str(uuid.uuid4()),
                run_id=run_id,
                tool_name=tc.tool_name,
                arguments=tc.arguments,
                result=tc.result,
                status=tc.status,
                duration_ms=tc.duration_ms,
            )
        )
    db.commit()

    if result.final_response:
        db.add(Message(id=str(uuid.uuid4()), run_id=run_id, role="assistant", content=result.final_response))
        db.commit()

    return RunResponse(
        run_id=run_id,
        agent=agent.name,
        status=result.status,
        response=result.final_response,
        duration_ms=duration_ms,
        tool_calls=[ToolCallResponse(tool=tc.tool_name, status=tc.status) for tc in result.tool_calls],
    )
