import json

from agent.sandbox.manager import SandboxManager


def execute_code(
    code: str,
    sandbox_manager: SandboxManager,
    timeout_seconds: int = 30,
) -> str:
    """Execute Python code inside the active E2B sandbox."""

    result = sandbox_manager.execute(code, timeout=timeout_seconds)

    return json.dumps({
        "output": "".join(result.get("stdout", []))[:2000],
        "error": result.get("error")
                 or "".join(result.get("stderr", []))[:500]
                 or None,
        "success": result.get("success", False),
        "generated_files": result.get("generated_files", []),
        "sync_error": result.get("sync_error"),
    })
