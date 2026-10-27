import hashlib
import os
from threading import RLock

from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from pathlib import Path
load_dotenv()
from langfuse import observe

class SandboxManager:
    """
    Manages one persistent E2B sandbox per agent session.

    Responsibilities:
    - Lazy sandbox creation
    - Sandbox reuse
    - Code execution
    - Cleanup
    """

    def __init__(self):
        if not os.getenv("E2B_API_KEY"):
            raise RuntimeError("E2B_API_KEY is missing")

        self._sandbox = None
        self._lock = RLock()
        self._synced_outputs = {}

    def start(self):
        with self._lock:
            if self._sandbox is None:
                self._sandbox = Sandbox.create(timeout=300)

                # Create output directory inside E2B
                self._sandbox.files.make_dir("/home/user/outputs")

            return self._sandbox
    
    @observe(name="sandbox-manager", as_type="span")
    def execute(self, code: str, timeout:int) -> dict:
        if not isinstance(code, str) or not code.strip():
            return {
                "success": False,
                "error": "Python code cannot be empty",
            }

        # Serialize calls to the same persistent Python kernel.
        with self._lock:
            sandbox = self.start()

            try:
                execution = sandbox.run_code(
                    code,
                    timeout=timeout,
                )

                # Automatically synchronize generated files
                try:
                    downloaded_files = self.sync_outputs()
                    sync_error = None
                except Exception:
                    downloaded_files = []
                    sync_error = "Output synchronization failed"

                return {
                    "success": execution.error is None,
                    "stdout": execution.logs.stdout,
                    "stderr": execution.logs.stderr,
                    "error": (
                        execution.error.name
                        + ": "
                        + execution.error.value
                        if execution.error
                        else None
                    ),
                    "text": execution.text,
                    "result_count": len(execution.results),
                    "generated_files": downloaded_files,
                    "sync_error": sync_error,
                }

            except Exception:
                # Do not return SDK exception details or secrets
                # to the LLM or user.
                self.close()
                return {
                    "success": False,
                    "error": "Sandbox execution failed",
                }

    def upload_file(self, local_path: str) -> str:
        """
        Upload a trusted local file to the sandbox.
        Only call this from your backend, not directly from LLM input.
        """
        with self._lock:
            sandbox = self.start()

            filename = os.path.basename(local_path)
            remote_path = f"/home/user/{filename}"

            with open(local_path, "rb") as file:
                sandbox.files.write(remote_path, file.read())

            return remote_path

    def close(self):
        with self._lock:
            if self._sandbox is not None:
                sandbox = self._sandbox
                self._sandbox = None
                try:
                    sandbox.kill()
                except Exception:
                    pass
            self._synced_outputs.clear()
                


    def download_file(self, remote_path: str) -> str:
        """
        Download generated files from E2B into workspace/outputs/.
        Prevent overwriting existing local files.
        """
        with self._lock:
            sandbox = self.start()

            # Only allow files from the sandbox output directory
            allowed_dir = Path("/home/user/outputs")
            remote = Path(remote_path)

            if (
                not remote.is_absolute()
                or remote == allowed_dir
                or allowed_dir not in remote.parents
            ):
                raise ValueError("File must be inside /home/user/outputs/")

            # Local output directory
            project_root = Path(__file__).resolve().parent.parent.parent
            output_dir = project_root / "workspace" / "outputs"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Original filename
            local_path = output_dir / remote.name

            # Check if a file with the same name already exists
            counter = 1

            while local_path.exists():
                local_path = output_dir / (
                    f"{remote.stem}_{counter}{remote.suffix}"
                )
                counter += 1

            # Download file from E2B
            content = sandbox.files.read(
                str(remote),
                format="bytes"
            )

            # Save locally
            local_path.write_bytes(content)

            return str(local_path)

    def sync_outputs(self) -> list[str]:
        """
        Synchronize new or modified E2B output files
        into the local workspace/outputs/ directory.
        """
        with self._lock:
            sandbox = self.start()

            remote_dir = "/home/user/outputs"
            downloaded = []

            files = sandbox.files.list(remote_dir)

            for entry in files:
                # Ignore directories
                entry_type = getattr(entry.type, "value", entry.type)

                if str(entry_type).lower() != "file":
                    continue

                remote_path = entry.path

                # Read contents
                content = sandbox.files.read(
                    remote_path,
                    format="bytes"
                )

                # Calculate file hash
                file_hash = hashlib.sha256(content).hexdigest()

                # Skip unchanged files
                if self._synced_outputs.get(remote_path) == file_hash:
                    continue

                # Download file
                local_path = self.download_file(remote_path)

                # Update tracking
                self._synced_outputs[remote_path] = file_hash

                downloaded.append(local_path)

            return downloaded

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
