# API Reference

Base URL: `http://localhost:8000` (backend).

All endpoints return JSON.

## Health

### `GET /health`

```json
{
  "status": "healthy",
  "timestamp": "2026-09-11T12:00:00Z",
  "version": "0.1.0"
}
```

## Agents

### `GET /agents`

List all agents. Each agent:

```json
{
  "id": "code-assistant",
  "name": "Code Assistant",
  "description": "...",
  "system_prompt": "...",
  "model": "ollama/qwen2.5:1.5b",
  "enabled": true,
  "created_at": "...",
  "updated_at": "..."
}
```

### `GET /agents/{agent_id}`

Single agent. `404` if not found.

### `POST /agents/{agent_id}/run`

Execute an agent. Body:

```json
{ "prompt": "Analyze main.py and identify potential problems" }
```

`400` if the agent is disabled, `404` if not found, `422` if prompt missing.

Response:

```json
{
  "run_id": "abc-123",
  "agent": "Code Assistant",
  "status": "success",
  "response": "...",
  "duration_ms": 2450,
  "tool_calls": [ { "tool": "read_file", "status": "success" } ]
}
```

`status` may be `success`, `error`, or `max_turns_exceeded`.

## Runs

### `GET /runs`

List all runs, newest first. Each run:

```json
{
  "id": "abc-123",
  "agent_id": "code-assistant",
  "prompt": "...",
  "status": "success",
  "model": "ollama/qwen2.5:1.5b",
  "duration_ms": 2450,
  "llm_requests": 2,
  "started_at": "...",
  "completed_at": "..."
}
```

### `GET /runs/{run_id}`

Full run detail (adds `final_response`, `error`).

### `GET /runs/{run_id}/tools`

Tool calls for a run, in execution order. Each tool call:

```json
{
  "id": "...",
  "tool_name": "read_file",
  "arguments": "{\"path\": \"main.py\"}",
  "result": "...",
  "status": "success",
  "duration_ms": 40
}
```

### `GET /runs/{run_id}/messages`

Full message transcript in chronological order:

```json
[
  { "id": "...", "role": "user", "content": "Analyze main.py", "created_at": "..." },
  { "id": "...", "role": "assistant", "content": "", "created_at": "..." },
  { "id": "...", "role": "tool", "content": "<tool result>", "created_at": "..." },
  { "id": "...", "role": "assistant", "content": "<final answer>", "created_at": "..." }
]
```

`404` if the run does not exist.

## Metrics

### `GET /metrics`

Aggregates across all runs and tool calls:

```json
{
  "total_runs": 12,
  "total_tool_calls": 18,
  "successful_runs": 10,
  "failed_runs": 1,
  "success_rate": 83.3,
  "avg_duration_ms": 2450.5,
  "avg_llm_requests": 2.25,
  "avg_tool_calls_per_run": 1.5,
  "error_tool_calls": 2,
  "agents": 1,
  "last_run_at": "2026-09-11T12:00:00Z"
}
```

## Errors

Errors use FastAPI's default shape with a `detail` field:

```json
{ "detail": "Run 'abc' not found" }
```