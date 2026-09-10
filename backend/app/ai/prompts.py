from app.db.models import Agent


def build_system_prompt(agent: Agent) -> str:
    return agent.system_prompt


def build_tool_definitions() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories at a given path within the workspace. Returns directory listing or file info.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path within the workspace directory. Defaults to root if empty.",
                        }
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file within the workspace. Returns the file content as text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file within the workspace directory.",
                        }
                    },
                    "required": ["path"],
                },
            },
        },
    ]
