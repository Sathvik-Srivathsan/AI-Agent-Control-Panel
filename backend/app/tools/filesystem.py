import os
from pathlib import Path
from app.tools.registry import register_tool
from app.core.config import settings


def _validate_path(requested: str) -> Path:
    workspace = settings.workspace_path
    resolved = (workspace / requested).resolve()
    if not str(resolved).startswith(str(workspace)):
        raise PermissionError(f"Path traversal denied: {requested}")
    return resolved


@register_tool("list_files")
def list_files(path: str = "") -> str:
    target = _validate_path(path) if path else settings.workspace_path
    if not target.exists():
        return f"Error: path '{path}' does not exist"
    if not target.is_dir():
        return f"Error: path '{path}' is not a directory"
    entries = sorted(os.listdir(target))
    if not entries:
        return "(empty directory)"
    lines = []
    for entry in entries:
        full = target / entry
        prefix = "d " if full.is_dir() else "f "
        lines.append(f"{prefix}{entry}")
    return "\n".join(lines)


@register_tool("read_file")
def read_file(path: str) -> str:
    target = _validate_path(path)
    if not target.exists():
        return f"Error: file '{path}' not found"
    if not target.is_file():
        return f"Error: path '{path}' is not a file"
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: file '{path}' is not a text file"
    return content
