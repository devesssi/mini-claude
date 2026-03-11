import subprocess

def run_command(command):
    """Executes a shell command and returns output/errors."""
    try:
        # Use shell=True for Windows compatibility (PowerShell/CMD)
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}