import json
import time
from dataclasses import dataclass, field
from typing import Any
from app.ai.client import LLMClient, LLMMessage, LLMResponse
from app.ai.prompts import build_system_prompt, build_tool_definitions
from app.tools.registry import execute_tool, list_tools
from app.db.models import Agent


MAX_TOOL_ROUNDS = 10


@dataclass
class ToolCallRecord:
    tool_name: str
    arguments: str
    result: str
    status: str
    duration_ms: int


@dataclass
class AgentRunResult:
    final_response: str
    status: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    llm_requests: int = 0
    error: str | None = None


def run_agent(agent: Agent, prompt: str, llm_client: LLMClient) -> AgentRunResult:
    messages: list[LLMMessage] = [
        LLMMessage(role="system", content=build_system_prompt(agent)),
        LLMMessage(role="user", content=prompt),
    ]

    tool_defs = build_tool_definitions()
    tool_call_records: list[ToolCallRecord] = []
    llm_requests = 0

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            llm_requests += 1
            response: LLMResponse = llm_client.chat(messages, tools=tool_defs)
        except Exception as e:
            return AgentRunResult(
                final_response="",
                status="error",
                tool_calls=tool_call_records,
                llm_requests=llm_requests,
                error=str(e),
            )

        if response.tool_calls:
            messages.append(
                LLMMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=[
                        {"id": tc.id, "function": {"name": tc.function, "arguments": tc.arguments}}
                        for tc in response.tool_calls
                    ],
                )
            )

            for tc in response.tool_calls:
                start = time.time()
                try:
                    args = json.loads(tc.arguments)
                except json.JSONDecodeError:
                    args = {}

                try:
                    result = execute_tool(tc.function, args)
                    status = "success"
                except Exception as e:
                    result = f"Error: {e}"
                    status = "error"

                duration_ms = int((time.time() - start) * 1000)
                tool_call_records.append(
                    ToolCallRecord(
                        tool_name=tc.function,
                        arguments=json.dumps(args),
                        result=result,
                        status=status,
                        duration_ms=duration_ms,
                    )
                )

                messages.append(
                    LLMMessage(
                        role="tool",
                        content=result,
                        tool_call_id=tc.id,
                    )
                )
        else:
            return AgentRunResult(
                final_response=response.content or "",
                status="success",
                tool_calls=tool_call_records,
                llm_requests=llm_requests,
            )

    return AgentRunResult(
        final_response=response.content or "",
        status="max_turns_exceeded",
        tool_calls=tool_call_records,
        llm_requests=llm_requests,
    )
