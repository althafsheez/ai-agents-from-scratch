import os
import json

def list_files(directory: str) -> str:
    """List files in a directory."""
    try:
        files = os.listdir(directory)
        return json.dumps({"files": files, "directory": directory})
    except Exception as e:
        return json.dumps({"error": str(e)})

def read_file(filepath: str) -> str:
    """Read the contents of a file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return json.dumps({"content": content, "filepath": filepath})
    except Exception as e:
        return json.dumps({"error": str(e)})

TOOLS = {
    "list_files": {
        "function": list_files,
        "description": "List files in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to list"}
            },
            "required": ["directory"]
        }
    },
    "read_file": {
        "function": read_file,
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Full path to the file"}
            },
            "required": ["filepath"]
        }
    }
}