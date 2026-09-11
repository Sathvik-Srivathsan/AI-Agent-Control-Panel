import os
import json
import pytest
from unittest.mock import MagicMock, patch

os.environ["WORKSPACE_DIR"] = "./test_workspace"

from app.ai.agent import run_agent, AgentRunResult
from app.ai.client import LLMMessage, LLMResponse, LLMToolCall, LLMClient
from app.db.models import Agent


def make_agent():
    return Agent(
        id="test-agent",
        name="Test Agent",
        system_prompt="You are a test agent.",
        model="test-model",
    )


def test_run_agent_simple_response():
    agent = make_agent()
    mock_response = LLMResponse(content="Done", finish_reason="stop")

    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat.return_value = mock_response

    result = run_agent(agent, "test prompt", mock_client)

    assert isinstance(result, AgentRunResult)
    assert result.status == "success"
    assert result.final_response == "Done"
    assert len(result.tool_calls) == 0
    assert result.llm_requests == 1


def test_run_agent_with_tool_call():
    agent = make_agent()

    tool_response = LLMResponse(
        content=None,
        tool_calls=[LLMToolCall(id="call_1", function="list_files", arguments='{"path": ""}')],
        finish_reason="tool_calls",
    )
    final_response = LLMResponse(content="Found files", finish_reason="stop")

    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat.side_effect = [tool_response, final_response]

    with patch("app.ai.agent.execute_tool") as mock_exec:
        mock_exec.return_value = "f main.py\nf utils.py"
        result = run_agent(agent, "list files", mock_client)

    assert result.status == "success"
    assert result.final_response == "Found files"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].tool_name == "list_files"
    assert result.llm_requests == 2
    assert len(result.messages) == 4
    assert result.messages[0].role == "system"
    assert result.messages[1].role == "user"
    assert result.messages[2].role == "assistant"
    assert result.messages[2].tool_calls[0]["function"]["name"] == "list_files"
    assert result.messages[3].role == "tool"
    assert result.messages[3].content == "f main.py\nf utils.py"


def test_run_agent_tool_error():
    agent = make_agent()

    tool_response = LLMResponse(
        content=None,
        tool_calls=[LLMToolCall(id="call_1", function="read_file", arguments='{"path": "missing.txt"}')],
        finish_reason="tool_calls",
    )
    final_response = LLMResponse(content="File not found", finish_reason="stop")

    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat.side_effect = [tool_response, final_response]

    with patch("app.ai.agent.execute_tool") as mock_exec:
        mock_exec.side_effect = ValueError("File not found")
        result = run_agent(agent, "read missing", mock_client)

    assert result.status == "success"
    assert result.tool_calls[0].status == "error"


def test_run_agent_llm_error():
    agent = make_agent()

    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat.side_effect = Exception("Connection refused")

    result = run_agent(agent, "test", mock_client)

    assert result.status == "error"
    assert "Connection refused" in result.error


def test_run_agent_max_turns():
    agent = make_agent()

    tool_response = LLMResponse(
        content=None,
        tool_calls=[LLMToolCall(id="call_1", function="list_files", arguments='{"path": ""}')],
        finish_reason="tool_calls",
    )

    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat.return_value = tool_response

    with patch("app.ai.agent.execute_tool") as mock_exec:
        mock_exec.return_value = "result"
        result = run_agent(agent, "loop forever", mock_client)

    assert result.status == "max_turns_exceeded"
    assert result.llm_requests == 10
