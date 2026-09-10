from pydantic import BaseModel


class RunRequest(BaseModel):
    prompt: str


class ToolCallResponse(BaseModel):
    tool: str
    status: str


class RunResponse(BaseModel):
    run_id: str
    agent: str
    status: str
    response: str
    duration_ms: int
    tool_calls: list[ToolCallResponse]
