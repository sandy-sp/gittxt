# src/gittxt-ui/backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import tempfile
import shutil

from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder

app = FastAPI()

class ScanRequest(BaseModel):
    repo_url: str
    file_types: str = "code,docs"
    output_format: str = "txt"

@app.post("/scan")
def scan_repo(request: ScanRequest):
    """
    Endpoint that:
      1. Clones or uses a local path
      2. Runs Gittxt's Scanner + OutputBuilder
      3. Returns a summary
    """
    # 1) Prepare a temporary directory to store or clone the repo
    tmp_dir = tempfile.mkdtemp(prefix="gittxt-")

    try:
        # 2) Use RepositoryHandler to handle local or remote
        repo_handler = RepositoryHandler(
            source=request.repo_url,  # e.g. "https://github.com/owner/repo.git"
            branch=None               # optional override of branch
        )
        repo_path, subdir, is_remote = repo_handler.get_local_path()
        # Gittxt returns (repo_path, subdir, is_remote)
        # If it's a subdir, combine them
        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        # 3) Set up the Scanner with user-provided file_types
        scanner = Scanner(
            root_path=scan_root.resolve(),
            include_patterns=[],
            exclude_patterns=[".git", "node_modules"],  # you can refine further
            size_limit=None,
            file_types=request.file_types.split(","),   # e.g. ["code","docs"]
            progress=False
        )
        valid_files, tree_summary = scanner.scan_directory()
        if not valid_files:
            return {
                "success": False,
                "message": "No valid files found based on filters.",
                "file_count": 0,
                "tree_summary": tree_summary
            }

        # 4) Build outputs (OutputBuilder)
        #    We specify a second temp folder for actual output (avoid messing the original clone)
        output_temp = Path(tmp_dir) / "outputs"
        output_temp.mkdir(parents=True, exist_ok=True)
        builder = OutputBuilder(
            repo_name="my-scanned-repo",
            output_dir=output_temp,
            output_format=request.output_format
        )
        builder.generate_output(valid_files, scan_root)

        # Optionally read back JSON result if we want to return detailed contents
        # This depends on request.output_format. For demonstration, let's handle JSON only:
        details = {}
        if "json" in request.output_format:
            from pathlib import Path
            json_file = output_temp / "json" / "my-scanned-repo.json"
            if json_file.exists():
                import json
                details = json.loads(json_file.read_text(encoding="utf-8"))

        return {
            "success": True,
            "message": "Scan complete",
            "file_count": len(valid_files),
            "tree_summary": tree_summary,
            "details": details  # optional
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        # 5) Cleanup: If it’s a remote, Gittxt had to clone the repo; we can remove it
        #    Or remove any ephemeral folders we created.
        #    The Gittxt repository handler also tries to clean up after scanning, but let’s do final pass:
        if Path(repo_path).exists() and is_remote:
            shutil.rmtree(repo_path, ignore_errors=True)
        # also remove `tmp_dir` if you like:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.get("/")
def root():
    return {"message": "Gittxt-FastAPI is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
