# AI Agent Control Panel

A lightweight full-stack web application for creating, configuring, running, and monitoring AI agents.

## Overview

This project demonstrates AI agent workflows, LLM integration, tool/function calling, model/provider abstraction, execution logging, and basic metrics through a unified web interface.

The application uses **OmniRoute** as an OpenAI-compatible model gateway, allowing it to work with cloud LLM providers, local Ollama models, and other OpenAI-compatible providers without hardcoding the LLM provider.

## Architecture

```
User
  |
  v
Frontend  (React, :5173)
  |
  v
FastAPI   (:8080)
  |
  v
Agent Controller
  |
  v
OmniRoute (:20128)
  |
  +---- Cloud LLM
  |
  +---- Local Ollama LLM (:11434)  ->  qwen2.5:1.5b
  |
  v
Agent response/tool calls
```
```
┌──────┐     ┌─────────┐     ┌─────────┐     ┌───────────┐     ┌────────┐     ┌──────┐
│ User │     │ Next.js │     │ FastAPI │     │ OmniRoute │     │ Ollama │     │ Qwen │
└───┬──┘     └────┬────┘     └────┬────┘     └─────┬─────┘     └────┬───┘     └───┬──┘
    │             │               │                │                │             │
    │ Submit agent request        │                │                │             │
    ├────────────►│               │                │                │             │
    │             │               │                │                │             │
    │             │ POST /agents/{id}/run          │                │             │
    │             ├──────────────►│                │                │             │
    │             │               │                │                │             │
    │             │               │ LLM request + API key           │             │
    │             │               ├───────────────►│                │             │
    │             │               │                │                │             │
    │             │               │                │ Route request  │             │
    │             │               │                ├───────────────►│             │
    │             │               │                │                │             │
    │             │               │                │                │ Generate response
    │             │               │                │                ├────────────►│
    │             │               │                │                │             │
    │             │               │                │                │ Model response
    │             │               │                │                │◄┈┈┈┈┈┈┈┈┈┈┈┈┤
    │             │               │                │                │             │
    │             │               │                │ Response       │             │
    │             │               │                │◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┤             │
    │             │               │                │                │             │
    │             │               │ LLM response   │                │             │
    │             │               │◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┤                │             │
    │             │               │                │                │             │
    │             │ Agent result  │                │                │             │
    │             │◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┤                │                │             │
    │             │               │                │                │             │
    │ Display response            │                │                │             │
    │◄┈┈┈┈┈┈┈┈┈┈┈┈┤               │                │                │             │
    │             │               │                │                │             │
```
SQLite stores:

- agents
- runs (including LLM request count per run)
- tool calls
- messages (full execution transcript)

## Technology Stack

- **Backend:** Python, FastAPI, Pydantic, SQLite, SQLAlchemy
- **Frontend:** React, Vite
- **AI:** OpenAI-compatible API via OmniRoute → local Ollama

## Project Structure

```
project-root/
    backend/
        app/
            main.py
            api/
                routes_agents.py
                routes_runs.py
            ai/
                client.py
                agent.py
                prompts.py
            tools/
                registry.py
                filesystem.py
            db/
                database.py
                models.py
                seed.py
            schemas/
                runs.py
            core/
                config.py
        tests/
            conftest.py
            test_health.py
            test_agents.py
            test_ai.py
            test_tools.py
            test_agent.py
            test_runs.py
            test_run_history.py
        requirements.txt
    frontend/
        src/
            api/client.js
            components/Layout.jsx
            pages/Dashboard.jsx
            pages/AgentList.jsx
            pages/AgentDetail.jsx
            pages/RunHistory.jsx
            pages/RunDetail.jsx
            App.jsx
            App.css
    docs/
        architecture.md
        api.md
    workspace/
    .env.example
    .gitignore
    AGENTS.md
    README.md
    start-all.cmd
    start-all.ps1
```

## Setup

### Prerequisites

- Python 3.11+
- OmniRoute (running and accessible)

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your OmniRoute configuration:

```
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=your-api-key
MODEL=your-model-name
WORKSPACE_DIR=./workspace
```

### Local model (Ollama) setup

1. [Install Ollama](https://ollama.com) and pull a model with tool-calling support:

   ```bash
   ollama pull qwen2.5:1.5b
   ```

2. [Install OmniRoute](https://omniroute.ai) or use the bundled launcher docs, then in
   its dashboard:
   - **Providers → Add provider** → pick **Ollama**, set base URL `http://localhost:11434`,
     no API key.
   - **API Manager** → create an API key (used as `OMNIROUTE_API_KEY`).
3. Point `.env` at the local stack:

   ```
   OMNIROUTE_BASE_URL=http://localhost:20128/v1
   OMNIROUTE_API_KEY=your-omniroute-key
   MODEL=ollama/qwen2.5:1.5b
   ```

4. (Recommended on low-RAM machines) limit Ollama: `setx OLLAMA_CONTEXT_LENGTH 4096`
   and `setx OLLAMA_KV_CACHE_TYPE q8_0`, then restart Ollama.

### Running Everything

Double-click `start-all.cmd`, or run `start-all.ps1`. It starts
OmniRoute/backend/frontend, skipping any port that is already listening.

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Running Tests

```bash
cd backend
pytest
```

## API Endpoints

- `GET /health` - Health check
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get agent details
- `POST /agents/{agent_id}/run` - Execute an agent with a prompt
- `GET /runs` - List all runs
- `GET /runs/{run_id}` - Get run details
- `GET /runs/{run_id}/tools` - Get tool calls for a run
- `GET /runs/{run_id}/messages` - Get the full message transcript for a run
- `GET /metrics` - Aggregated metrics across all runs and tool calls

Full reference: [`docs/api.md`](docs/api.md).

### Example: Run an Agent

```bash
curl -X POST http://localhost:8000/agents/code-assistant/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze main.py and identify potential problems"}'
```

Response:

```json
{
  "run_id": "abc-123",
  "agent": "Code Assistant",
  "status": "success",
  "response": "...",
  "duration_ms": 2450,
  "tool_calls": [
    {
      "tool": "read_file",
      "status": "success"
    }
  ]
}
```

## Monitoring

- **Dashboard** shows live backend status plus metric cards (success rate, average
  latency, tool calls/run, LLM requests/run, failed runs).
- **Run Details** renders a vertical execution timeline (LLM requests, tool calls,
  results, final response) and the full message transcript.
- **Metrics endpoint** (`GET /metrics`) aggregation is described in `docs/api.md`.

## Agents

### Code Assistant

- **Purpose:** Analyzes source code using controlled filesystem tools
- **Tools:** `list_files`, `read_file`
- **Behavior:** Inspects files before making claims, identifies bugs and maintainability issues, never modifies files

## Security

- Tools operate only within a configured workspace directory
- Path traversal is rejected (e.g., `../`, absolute paths outside workspace)
- API keys are never exposed in responses
- No unrestricted filesystem access
- No arbitrary shell command execution
- Registered tool execution only
