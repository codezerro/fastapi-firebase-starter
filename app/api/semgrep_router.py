from fastapi import APIRouter, HTTPException
import asyncio
import json
import os
from fastapi.responses import JSONResponse
from pathlib import Path

semgrep_routner = APIRouter()


@semgrep_routner.get("/health")
async def semgrep_health():
    return {"status": "healthy"}



# Target directory to scan
REPORT_PATH = "report.json"

DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = DIR / "scanning_projects" / "langfuse-master"
TARGET_DIR = BASE_DIR

print(BASE_DIR)


@semgrep_routner.post("/scan")
async def run_semgrep_scan():
    # Verify target directory exists
    if not os.path.exists(TARGET_DIR):
        raise HTTPException(status_code=404, detail=f"Target directory {TARGET_DIR} not found")

    # Construct the arguments matching your exact CLI command
    cmd = [
        "semgrep",
        "--config", "p/python",
        "--config", "p/security-audit",
        "--config", "p/python-command-injection",
        "--config", "p/secrets",
        "--json",
        "-o", REPORT_PATH,
        TARGET_DIR
    ]

    try:
        # Run non-blocking subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for semgrep to complete
        stdout, stderr = await process.communicate()

        # Semgrep exit codes: 0 = no find, 1 = findings found (unless --error is passed)
        if process.returncode not in [0, 1]:
            error_msg = stderr.decode().strip()
            raise HTTPException(status_code=500, detail=f"Semgrep failed: {error_msg}")

        # Read and parse the generated JSON file
        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, "r") as f:
                report_data = json.load(f)
            return JSONResponse(content={"status": "success", "results": report_data})
        
        raise HTTPException(status_code=500, detail="Scan completed but report file was not generated.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
