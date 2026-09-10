# AI Agent Control Panel

## 1. Project Goal

Build a lightweight full-stack web application for creating, configuring, running, and monitoring AI agents.

The project is intended as a practical AI engineering and software engineering portfolio project.

The application should demonstrate:

- AI agent workflows
- LLM integration
- tool/function calling
- model/provider abstraction
- AI workflow execution
- execution logging
- basic evaluation/metrics
- REST API development
- SQLite persistence
- modern web frontend
- eventual MCP integration

The application must be designed so that the LLM provider is NOT hardcoded into the application.

The primary inference gateway will be OmniRoute.

OmniRoute should act as an OpenAI-compatible model gateway between the application and the actual LLM provider.

Possible providers include:

- Cloud LLM providers through OmniRoute
- Local Ollama models through OmniRoute
- Other OpenAI-compatible providers supported by OmniRoute

The application itself should communicate with a single OpenAI-compatible endpoint.

---

# 2. IMPORTANT DEVELOPMENT PHILOSOPHY

Do NOT attempt to build the complete system immediately.

Build incrementally.

The first milestone is a small but fully functional MVP that can:

1. Start the backend.
2. Connect to OmniRoute.
3. Run one agent.
4. Give the agent a small set of tools.
5. Execute a tool call.
6. Return the final response.
7. Store the execution in SQLite.
8. Expose the result through an API.

Only after that works should the frontend become the primary focus.

Do not introduce unnecessary complexity.

Do not build a distributed architecture.

Do not build authentication initially.

Do not build Kubernetes/Docker infrastructure unless it becomes necessary.

Do not implement our own LLM.

Do not implement our own LLM routing system because OmniRoute already provides that functionality.

---

# 3. Target Architecture

Initial architecture:

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

SQLite stores:

- agents
- runs
- tool calls
- messages
- errors
- basic metrics

Later architecture:

Next.js
    |
    v
FastAPI
    |
    +--------------------+
    |                    |
    v                    v
Agent Controller      SQLite
    |
    v
OmniRoute
    |
    +---- Cloud models
    |
    +---- Local models
    |
    v
LLM
    |
    +---- Internal tools
    |
    +---- MCP tools

---

# 4. Technology Stack

## Backend

Python

FastAPI

Pydantic

SQLite

SQLAlchemy or SQLModel

httpx or an appropriate OpenAI-compatible Python client

pytest

## Frontend

Use React initially.

Use Next.js when the frontend is rebuilt/refactored into the final architecture.

Do not make the backend dependent on the frontend.

The API must remain independently usable.

## AI

OpenAI-compatible API interface.

OmniRoute as the model gateway.

The actual model should be configurable through environment variables.

Example conceptual configuration:

OMNIROUTE_BASE_URL=http://localhost:20128/v1

OMNIROUTE_API_KEY=...

MODEL=...

Do not hardcode credentials.

---

# 5. MVP Scope

The MVP should contain ONE working agent.

Agent name:

Code Assistant

Purpose:

Analyze user-provided code or a local project file using controlled tools.

Initial tools:

1. list_files
2. read_file

The agent must NOT have unrestricted filesystem access.

Tools must operate only inside a configured workspace directory.

Example:

WORKSPACE_DIR=./workspace

The agent should not be able to access arbitrary paths on the user's computer.

---

# 6. Agent Execution Flow

Example:

User:

"Analyze main.py and identify potential problems."

Flow:

1. FastAPI receives the request.
2. Agent Controller loads the selected agent configuration.
3. Agent Controller sends the conversation and available tools to the configured LLM through OmniRoute.
4. LLM decides whether a tool is required.
5. Application validates the requested tool.
6. Application executes the tool.
7. Tool result is returned to the LLM.
8. LLM may request another tool.
9. Application repeats the controlled tool loop.
10. LLM produces a final response.
11. Application stores the execution.
12. API returns the final response and execution metadata.

---

# 7. Tool Execution Safety

Tools must be explicitly registered.

Example conceptual registry:

tools = {
    "list_files": list_files,
    "read_file": read_file
}

The LLM must never directly execute arbitrary Python.

The LLM must never directly execute arbitrary shell commands.

The LLM must never receive unrestricted filesystem access.

Path validation must prevent directory traversal.

Reject paths such as:

../
../../
absolute paths outside the workspace

Resolve the requested path and verify that it remains inside WORKSPACE_DIR.

This is a portfolio project, so basic security-conscious engineering should be visible.

---

# 8. Agent Configuration

Agents should eventually be stored in SQLite.

Each agent should have:

- id
- name
- description
- system_prompt
- model
- enabled
- created_at
- updated_at

Example:

Code Assistant

Description:
Analyzes source code using controlled filesystem tools.

Model:
Configured through environment/configuration.

Tools:
- list_files
- read_file

---

# 9. Database Models

Start with these tables.

## agents

id
name
description
system_prompt
model
enabled
created_at
updated_at

## runs

id
agent_id
prompt
final_response
status
model
started_at
completed_at
duration_ms
error

## tool_calls

id
run_id
tool_name
arguments
result
status
started_at
completed_at
duration_ms

## messages

id
run_id
role
content
created_at

Keep the schema simple.

Do not over-normalize.

---

# 10. REST API

Initial endpoints:

GET /health

GET /agents

GET /agents/{agent_id}

POST /agents/{agent_id}/run

GET /runs

GET /runs/{run_id}

GET /runs/{run_id}/tools

The most important endpoint is:

POST /agents/{agent_id}/run

Example request:

{
  "prompt": "Analyze main.py"
}

Example conceptual response:

{
  "run_id": "123",
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

Do not expose internal API keys.

---

# 11. Frontend MVP

The frontend should initially be simple.

Pages/components:

Dashboard

Agent list

Agent detail

Agent execution screen

Run history

Run detail

The main execution screen should contain:

Agent selector

Model/provider information

Prompt input

Run button

Final response

Execution status

Tool-call timeline

Basic metrics

Example:

------------------------------------------------

AI AGENT CONTROL PANEL

Agents

[ Code Assistant ]

Agent:

Code Assistant

Model:

OmniRoute / configured model

Prompt:

[ Analyze main.py and identify potential bugs ]

[ RUN AGENT ]

Execution

Status: SUCCESS

Duration: 2.4s

Tool calls:

1. read_file
2. read_file

Response:

...

------------------------------------------------

---

# 12. Execution Timeline

Every agent run should produce an execution timeline.

Example:

RUN #14

12:31:02
REQUEST_RECEIVED

12:31:02
LLM_REQUEST

12:31:03
TOOL_CALL
read_file

12:31:03
TOOL_RESULT

12:31:04
LLM_REQUEST

12:31:04
FINAL_RESPONSE

12:31:04
RUN_COMPLETED

This should eventually be visualized in the frontend.

---

# 13. Basic Metrics

Track:

- execution duration
- number of LLM requests
- number of tool calls
- successful tool calls
- failed tool calls
- run success/failure

Eventually calculate:

- total runs
- successful runs
- failed runs
- success rate
- average latency
- average tool calls per run

Do not initially implement sophisticated evaluation models.

---

# 14. Error Handling

The system must handle:

- OmniRoute unavailable
- invalid model
- invalid agent
- invalid tool
- malformed tool arguments
- file not found
- permission errors
- LLM timeout
- tool timeout
- invalid LLM response
- unexpected exceptions

Errors should:

1. Be logged.
2. Be associated with the run when applicable.
3. Produce a useful API response.
4. Never expose secrets.

---

# 15. Configuration

Use environment variables.

Create:

.env.example

Example:

OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=
MODEL=

WORKSPACE_DIR=./workspace

Do NOT commit .env.

Add .env to .gitignore.

Never place API keys in source code.

---

# 16. OmniRoute Integration

Treat OmniRoute as an external infrastructure dependency.

The application should only assume that it exposes an OpenAI-compatible API.

Create a dedicated module for the LLM client.

Example conceptual structure:

backend/
    app/
        ai/
            client.py
            agent.py
            prompts.py

The rest of the application should not contain OmniRoute-specific HTTP implementation.

This allows the model gateway to be replaced later without rewriting the agent system.

Do not implement routing, fallback logic, or provider management ourselves.

OmniRoute handles that layer.

---

# 17. Local Model Support

Local inference is optional.

The application should support it through OmniRoute/Ollama without changing application code.

The project should remain model-agnostic.

Example:

Application
    |
    v
OmniRoute
    |
    v
Ollama
    |
    v
Small local model

or:

Application
    |
    v
OmniRoute
    |
    v
Cloud model

The application should not assume that local inference is available.

---

# 18. MCP

MCP is NOT required for the first MVP.

Do not implement MCP during the initial build unless the basic agent/tool system is already working.

Later milestone:

Convert or expose selected tools through MCP.

Potential future tools:

- filesystem
- GitHub
- SQLite
- documentation
- project analysis

The architecture should keep tool interfaces clean enough that MCP integration can be added later.

---

# 19. Testing

At minimum create tests for:

- health endpoint
- agent retrieval
- invalid agent
- path traversal prevention
- list_files tool
- read_file tool
- successful agent run
- failed tool execution
- database persistence

Mock LLM responses in unit tests.

Tests must NOT require a real cloud LLM.

Do not make the entire test suite dependent on OmniRoute being online.

---

# 20. Project Structure

Prefer this structure:

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
                repositories.py

            schemas/
                agents.py
                runs.py

            core/
                config.py
                security.py

        tests/

        requirements.txt

    frontend/
        ...

    workspace/

    docs/
        architecture.md
        api.md

    .env.example
    .gitignore
    AGENTS.md
    README.md

Do not create unnecessary directories.

---

# 21. Development Order

Follow this order.

## Phase 1

Create repository.

Create Python backend.

Create FastAPI application.

Add /health.

Verify backend runs.

## Phase 2

Add SQLite.

Create database models.

Create agent seed data.

Create agent API.

## Phase 3

Implement OmniRoute client.

Implement configurable model.

Verify a simple LLM request.

## Phase 4

Implement agent execution loop.

Implement tool registry.

Implement list_files.

Implement read_file.

Implement controlled tool execution.

## Phase 5

Persist runs and tool calls.

Implement run history endpoints.

## Phase 6

Write tests.

Fix error handling.

Create README.

At this point the backend MVP is considered complete.

## Phase 7

Build simple frontend.

Connect it to FastAPI.

Create agent dashboard.

Create execution interface.

Create run history.

## Phase 8

Polish UI.

Improve execution timeline.

Add basic metrics.

Improve documentation.

## Phase 9

Optional:

MCP integration.

Additional agents.

Additional tools.

Evaluation features.

---

# 22. Initial Agents

Only implement ONE initially.

## Code Assistant

System behavior:

You are a code analysis assistant.

You can inspect files using the available controlled filesystem tools.

You must not invent file contents.

You must inspect relevant files before making claims about them.

You should explain findings clearly.

You should identify potential bugs, maintainability issues, and suspicious patterns.

You must not modify files.

Tools:

list_files
read_file

Later agents can include:

Data Analyst

Documentation Agent

Research Agent

Test Generation Agent

But these are future milestones.

---

# 23. Definition of Done for MVP

The MVP is DONE when all of the following work:

1. FastAPI starts successfully.
2. SQLite database initializes.
3. At least one agent exists.
4. OmniRoute can be configured through environment variables.
5. The application can send a prompt to the configured LLM.
6. The LLM can request a registered tool.
7. The application executes the tool safely.
8. Tool results return to the LLM.
9. The final response reaches the API.
10. The complete run is stored in SQLite.
11. Tool calls are stored.
12. Errors are handled.
13. Tests pass.
14. README explains setup.
15. No secrets are committed.

Only after these are complete should additional features be added.

---

# 24. README Requirements

The README should explain:

- What the project is
- Why it exists
- Architecture
- Technology stack
- Features
- Setup
- OmniRoute configuration
- Running the backend
- Running the frontend
- Running tests
- Example agent execution
- Security considerations
- Future roadmap

Include an architecture diagram using Mermaid if useful.

Do not claim features that have not actually been implemented.

---

# 25. Resume Positioning

The project should eventually support a resume entry similar to:

AI Agent Control Panel
Next.js, React, FastAPI, Python, SQLite, LLMs, OmniRoute

Built a full-stack AI agent control platform for configuring, executing, and monitoring tool-enabled LLM workflows, with FastAPI REST APIs, SQLite persistence, controlled tool execution, and an OpenAI-compatible model gateway.

Do not add this to the README as a fake completed achievement.

The resume wording is only a target for the final implemented system.

---

# 26. Critical Rules for the Coding Agent

Do not over-engineer.

Do not implement future features before the MVP works.

Do not create placeholder functionality and claim it works.

Do not silently skip errors.

Do not hardcode credentials.

Do not expose environment secrets.

Do not allow unrestricted filesystem access.

Do not execute arbitrary shell commands from LLM output.

Do not add dependencies without a reason.

Prefer simple, readable Python.

Prefer small modules.

Keep frontend and backend independently runnable.

When uncertain about a design decision, choose the simplest implementation that preserves future extensibility.

Before declaring a milestone complete, actually run the relevant tests or commands.

---

# 27. First Task

Start with Phase 1 only.

Before writing substantial code:

1. Inspect the current repository.
2. Check installed Python and Node versions.
3. Check whether FastAPI is installed.
4. Check whether OmniRoute is installed/running.
5. Check whether Node/npm is available.
6. Check whether the repository is empty or already contains files.
7. Create a short implementation plan.

Then implement ONLY the initial backend skeleton:

- FastAPI
- configuration
- /health
- project structure
- requirements
- .env.example
- .gitignore
- initial README
- tests for /health

Do not implement the frontend yet.

Do not implement MCP yet.

Do not implement multiple agents yet.

Do not implement authentication yet.

After completing Phase 1, report:

- files created
- commands executed
- tests executed
- test results
- anything blocking the next phase

Then wait for the next instruction.

---

# 28. Development Principle

The final project should feel like a real internal engineering tool rather than a generic AI chatbot.

The core idea is:

"Give engineers a simple interface for running, inspecting, and eventually evaluating AI agents and their tool-driven workflows."

Build the smallest useful version first.

Then progressively evolve it into a polished AI engineering platform.