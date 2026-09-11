# AGENTS.md

Guidance for AI agents working on this project.

## Project

Full-stack web app for running/monitoring AI agents with tool calling.

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, SQLite (`backend/agent_control.db`)
- **Frontend:** React + Vite
- **LLM:** OpenAI-compatible chain `App → OmniRoute (:20128) → Ollama (:11434) → qwen2.5:1.5b`
- Live ports: backend `:8080`, frontend `:5173`, OmniRoute `:20128`, Ollama `:11434`

## Commands

- Backend tests: `cd backend && python -m pytest -q`
- Backend dev server: `cd backend && uvicorn app.main:app --reload`
- Frontend build: `cd frontend && npm run build`
- Frontend dev server: `cd frontend && npm run dev`
- Launch everything: `start-all.cmd` (double-click) or `start-all.ps1` (skips
  already-running ports)

## Reasoning about the code

- An `Agent` has a `model` string (`ollama/qwen2.5:1.5b`) and `system_prompt`.
- `backend/app/ai/agent.py` is the agent loop; it returns `AgentRunResult` that includes
  the message transcript (`messages`) and `llm_requests` count.
- Tools are registered via `@register_tool` in `backend/app/tools/` and advertised to the
  model in `backend/app/ai/prompts.py:build_tool_definitions()`. Adding a tool = new
  module + one definition there.
- Runs, tool calls, and messages are persisted in SQLite. `GET /runs/{id}/messages`
  returns the transcript; `GET /metrics` aggregates stats.
- `Run.llm_requests` was added in Phase 8 with a guarded migration in
  `backend/app/db/database.py:init_db` — do not drop existing data in migrations.

## Conventions

- Frontend pages live in `frontend/src/pages`, API wrapper in `frontend/src/api/client.js`.
- Dark theme colors are CSS variables in `frontend/src/App.css`.
- Secrets (`.env`) are gitignored; never log or return API keys.
- No Docker/K8s, no auth, no pagination, no extra npm deps (project spec guardrails).
- `Prompt.md` (gitignored) is the design spec; `TEMP_web_search_plan.md` is a
  plan-only proposal for a future web-search tool (no implementation).

## Verification

Run backend tests + frontend build before finishing a task, then ask the user to
commit/push (user runs git).