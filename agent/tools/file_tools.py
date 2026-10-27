import os
import json
import pathlib

import json
from pathlib import Path

WORKSPACE = (Path(__file__).resolve().parents[1] / "workspace").resolve()


def list_files(directory: str = ".") -> str:
    """List files and directories inside the agent workspace only."""

    try:
        target = (WORKSPACE / directory).resolve()

        # Block access outside workspace
        if not target.is_relative_to(WORKSPACE):
            raise PermissionError("Access denied: Outside workspace")

        # Block hidden directories
        if any(part.startswith(".") for part in target.relative_to(WORKSPACE).parts):
            raise PermissionError("Access denied: Hidden directories are protected")

        if not target.is_dir():
            raise FileNotFoundError("Directory not found")

        files = [
            item.name
            for item in target.iterdir()
            if not item.name.startswith(".")
            and not item.is_symlink()
        ]

        return json.dumps({
            "files": sorted(files),
            "directory": str(target.relative_to(WORKSPACE))
        })

    except (OSError, ValueError) as e:
        return json.dumps({
            "error": str(e),
            "directory": directory
        })

def read_file(filepath: str) -> str:
    """Read a file only from the agent workspace."""
    try:
        path = (WORKSPACE / filepath).resolve()

        # Prevent access outside workspace
        if not path.is_relative_to(WORKSPACE):
            raise PermissionError("Access denied: Outside workspace")

        # Block hidden files such as .env
        if any(part.startswith(".") for part in path.relative_to(WORKSPACE).parts):
            raise PermissionError("Access denied: Hidden files are protected")

        if not path.is_file():
            raise FileNotFoundError("File not found")

        content = path.read_text(encoding="utf-8")

        return json.dumps({
            "content": content,
            "filepath": str(path.relative_to(WORKSPACE))
        })

    except (OSError, ValueError) as e:
        return json.dumps({
            "error": str(e)
        })

def write_file(filepath: str, content: str) -> str:
    """Write content to a file. Restricted to current directory tree."""
    # Prevent path traversal attacks
    safe_root = (pathlib.Path(__file__).resolve().parents[1] / "workspace").resolve()
    target = (safe_root / filepath).resolve()

    if not target.is_relative_to(safe_root):
        return json.dumps({
            "error": "Path traversal blocked",
            "filepath": filepath,
            "detail": "File paths must be within the current directory"
        })

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return json.dumps({
            "success": True,
            "filepath": str(target),
            "bytes_written": len(content.encode("utf-8"))
        })
    except PermissionError:
        return json.dumps({"error": "Permission denied", "filepath": filepath})
    except OSError as e:
        return json.dumps({"error": str(e), "filepath": filepath})