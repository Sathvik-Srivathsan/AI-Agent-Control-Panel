import os
import tempfile
import shutil
import pytest

os.environ["WORKSPACE_DIR"] = "./test_workspace"

from app.tools.registry import register_tool, get_tool, list_tools, execute_tool
from app.tools.filesystem import list_files, read_file, _validate_path
from app.core.config import settings


@pytest.fixture
def workspace():
    ws = settings.workspace_path
    ws.mkdir(parents=True, exist_ok=True)
    yield ws
    shutil.rmtree(ws, ignore_errors=True)


@pytest.fixture
def sample_workspace(workspace):
    (workspace / "hello.txt").write_text("hello world")
    (workspace / "subdir").mkdir()
    (workspace / "subdir" / "nested.txt").write_text("nested content")
    yield workspace
    shutil.rmtree(workspace, ignore_errors=True)


def test_register_and_get_tool():
    @register_tool("test_tool")
    def test_tool():
        return "ok"

    assert get_tool("test_tool") is not None


def test_list_tools():
    assert "list_files" in list_tools()
    assert "read_file" in list_tools()


def test_execute_tool():
    result = execute_tool("list_files", {"path": ""})
    assert isinstance(result, str)


def test_execute_unknown_tool_raises():
    with pytest.raises(ValueError, match="Unknown tool"):
        execute_tool("nonexistent_tool", {})


def test_validate_path_accepts_workspace(workspace):
    result = _validate_path("hello.txt")
    assert str(result).startswith(str(workspace))


def test_validate_path_rejects_traversal(workspace):
    with pytest.raises(PermissionError, match="traversal"):
        _validate_path("../../etc/passwd")


def test_validate_path_rejects_absolute():
    with pytest.raises(PermissionError, match="traversal"):
        _validate_path("/etc/passwd")


def test_list_files_empty(workspace):
    result = list_files("")
    assert "empty directory" in result


def test_list_files_with_content(sample_workspace):
    result = list_files("")
    assert "f hello.txt" in result
    assert "d subdir" in result


def test_list_files_nonexistent():
    result = list_files("nonexistent_dir_xyz")
    assert "Error" in result


def test_read_file_success(sample_workspace):
    result = read_file("hello.txt")
    assert result == "hello world"


def test_read_file_not_found():
    result = read_file("no_such_file.txt")
    assert "Error" in result


def test_read_file_directory():
    result = read_file("subdir")
    assert "Error" in result
