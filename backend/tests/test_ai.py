import os
import json
from unittest.mock import patch, MagicMock

os.environ["WORKSPACE_DIR"] = "./test_workspace"

from app.ai.client import LLMClient, LLMMessage, LLMResponse, LLMToolCall
from app.ai.prompts import build_system_prompt, build_tool_definitions
from app.db.models import Agent


def test_client_chat_returns_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "Hello"},
                "finish_reason": "stop",
            }
        ]
    }

    with patch("app.ai.client.httpx.Client") as MockClient:
        MockClient.return_value.__enter__ = MagicMock(return_value=MockClient.return_value)
        MockClient.return_value.__exit__ = MagicMock(return_value=False)
        MockClient.return_value.post.return_value = mock_response

        client = LLMClient()
        result = client.chat([LLMMessage(role="user", content="Hi")])

        assert isinstance(result, LLMResponse)
        assert result.content == "Hello"
        assert result.tool_calls == []


def test_client_chat_sends_correct_payload():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "test"},
                "finish_reason": "stop",
            }
        ]
    }

    with patch("app.ai.client.httpx.Client") as MockClient:
        MockClient.return_value.__enter__ = MagicMock(return_value=MockClient.return_value)
        MockClient.return_value.__exit__ = MagicMock(return_value=False)
        MockClient.return_value.post.return_value = mock_response

        client = LLMClient()
        client.chat([LLMMessage(role="user", content="test message")])

        call_args = MockClient.return_value.post.call_args
        payload = call_args[1]["json"]
        assert payload["messages"][0]["content"] == "test message"


def test_client_chat_parses_tool_calls():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "function": {
                                "name": "read_file",
                                "arguments": json.dumps({"path": "main.py"}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ]
    }

    with patch("app.ai.client.httpx.Client") as MockClient:
        MockClient.return_value.__enter__ = MagicMock(return_value=MockClient.return_value)
        MockClient.return_value.__exit__ = MagicMock(return_value=False)
        MockClient.return_value.post.return_value = mock_response

        client = LLMClient()
        result = client.chat([LLMMessage(role="user", content="read file")])

        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].id == "call_123"
        assert result.tool_calls[0].function == "read_file"
        assert result.tool_calls[0].arguments == json.dumps({"path": "main.py"})


def test_build_system_prompt():
    agent = Agent(
        id="test",
        name="Test",
        system_prompt="You are a test assistant.",
    )
    prompt = build_system_prompt(agent)
    assert prompt == "You are a test assistant."


def test_build_tool_definitions_returns_list():
    tools = build_tool_definitions()
    assert isinstance(tools, list)
    assert len(tools) == 2


def test_build_tool_definitions_contains_names():
    tools = build_tool_definitions()
    names = [t["function"]["name"] for t in tools]
    assert "list_files" in names
    assert "read_file" in names
