from dataclasses import dataclass, field
from typing import Any
import httpx
from app.core.config import settings


@dataclass
class LLMMessage:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class LLMToolCall:
    id: str
    function: str
    arguments: str


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[LLMToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    raw: dict = field(default_factory=dict)


class LLMClient:
    def __init__(self):
        self.base_url = settings.OMNIROUTE_BASE_URL.rstrip("/")
        self.api_key = settings.OMNIROUTE_API_KEY
        self.model = settings.MODEL

    def chat(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if tools:
            payload["tools"] = tools

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        tool_calls = []
        for tc in message.get("tool_calls", []):
            tool_calls.append(
                LLMToolCall(
                    id=tc["id"],
                    function=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                )
            )

        return LLMResponse(
            content=message.get("content"),
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason"),
            raw=data,
        )


llm_client = LLMClient()
