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
Frontend
  |
  v
FastAPI
  |
  v
Agent Controller
  |
  v
OmniRoute
  |
  +---- Cloud LLM
  |
  +---- Local Ollama LLM
  |
  v
Agent response/tool calls
```

SQLite stores:

- agents
- runs
- tool calls
- messages

## Technology Stack

- **Backend:** Python, FastAPI, Pydantic, SQLite, SQLAlchemy
- **Frontend:** React (planned)
- **AI:** OpenAI-compatible API via OmniRoute

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
    workspace/
    .env.example
    .gitignore
    README.md
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

## Development Phases

1. **Phase 1:** Backend skeleton with `/health` endpoint
2. **Phase 2:** SQLite database models and agent CRUD API
3. **Phase 3:** OmniRoute client and LLM integration
4. **Phase 4:** Agent execution loop with tool calling
5. **Phase 5:** Run history and persistence
6. **Phase 6:** Tests, error handling, documentation

## Future Roadmap

- React frontend with agent dashboard
- Execution timeline visualization
- Basic metrics and performance tracking
- MCP integration
- Additional agents and tools
- Authentication
- Next.js migration

## License

MIT
