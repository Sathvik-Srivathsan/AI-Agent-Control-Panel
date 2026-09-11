from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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
            "llm_requests": r.llm_requests,
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
        "llm_requests": run.llm_requests,
        "error": run.error,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


@router.get("/runs/{run_id}/tools")
def get_run_tools(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    tool_calls = (
        db.query(ToolCall)
        .filter(ToolCall.run_id == run_id)
        .order_by(ToolCall.started_at, text("rowid"))
        .all()
    )
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


@router.get("/runs/{run_id}/messages")
def get_run_messages(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    messages = (
        db.query(Message)
        .filter(Message.run_id == run_id)
        .order_by(Message.created_at, text("rowid"))
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    runs = db.query(Run).all()
    tool_calls = db.query(ToolCall).all()

    total_runs = len(runs)
    total_tool_calls = len(tool_calls)

    success_runs = sum(1 for r in runs if r.status == "success")
    error_runs = sum(1 for r in runs if r.status == "error")

    durations = [r.duration_ms for r in runs if r.duration_ms is not None]
    requests = [r.llm_requests for r in runs if r.llm_requests is not None]

    error_tool_calls = sum(1 for t in tool_calls if t.status == "error")

    return {
        "total_runs": total_runs,
        "total_tool_calls": total_tool_calls,
        "successful_runs": success_runs,
        "failed_runs": error_runs,
        "success_rate": round(success_runs / total_runs * 100, 1) if total_runs else 0.0,
        "avg_duration_ms": round(sum(durations) / len(durations), 1) if durations else 0.0,
        "avg_llm_requests": round(sum(requests) / len(requests), 2) if requests else 0.0,
        "avg_tool_calls_per_run": round(total_tool_calls / total_runs, 2) if total_runs else 0.0,
        "error_tool_calls": error_tool_calls,
        "agents": len({r.agent_id for r in runs}),
        "last_run_at": (
            max(r.started_at for r in runs if r.started_at).isoformat()
            if any(r.started_at for r in runs)
            else None
        ),
    }


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
    run.llm_requests = result.llm_requests
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

    for m in result.messages:
        if m.role in ("system", "user"):
            continue
        db.add(
            Message(
                id=str(uuid.uuid4()),
                run_id=run_id,
                role=m.role,
                content=m.content,
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
