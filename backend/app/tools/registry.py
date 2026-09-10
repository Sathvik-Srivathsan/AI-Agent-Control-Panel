from typing import Any, Callable

_registry: dict[str, Callable[..., str]] = {}


def register_tool(name: str):
    def decorator(func: Callable[..., str]):
        _registry[name] = func
        return func
    return decorator


def get_tool(name: str) -> Callable[..., str] | None:
    return _registry.get(name)


def list_tools() -> list[str]:
    return list(_registry.keys())


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    tool = get_tool(name)
    if not tool:
        raise ValueError(f"Unknown tool: {name}")
    return tool(**arguments)
