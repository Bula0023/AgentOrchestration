import subprocess
import os
import tempfile
from .schemas import CodeExecutionInput, CodeExecutionOutput

def execute_code(args: CodeExecutionInput) -> CodeExecutionOutput:
    # Create a temporary file to hold the code
    result = subprocess.run(
        ["docker",
         "run",
         "--rm",
         "--network", "none",
         "--memory", "256m",
            "--cpus", "0.5",
            "--read-only",
            "--user", "65534:65534",
            "python:3.12-slim",
            "python",
            "-c",
            args.code,],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return CodeExecutionOutput(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode
    )