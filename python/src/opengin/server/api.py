import logging
import os
import shutil
import tempfile
import uuid

import yaml
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from opengin.tracer.agents.orchestrator import Agent0

router = APIRouter()
logger = logging.getLogger(__name__)


# Initialize Orchestrator
# We use a fixed directory for the sandbox/pipelines
base_pipeline_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox", "pipelines"))
os.makedirs(base_pipeline_path, exist_ok=True)
agent0 = Agent0(base_path=base_pipeline_path)

# Temporary storage for upload before pipeline creation
UPLOAD_DIR = os.path.abspath(os.path.join(os.getcwd(), "sandbox", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ExtractionConfig(BaseModel):
    api_key: str
    metadata_yaml: str
    prompt: str


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and return a temporary file ID."""
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    return {"file_id": file_id, "filename": file.filename}


@router.get("/quick-setup")
async def quick_setup():
    """Setup a quick start environment with sample PDF and config."""
    # 1. Locate Sample File
    # Assuming running from 'python' dir, data is in '../data'
    # API is in src/opengin/server/api.py.
    # Current working dir is likely 'python' (where make run is executed).
    # So data is in '../data'.

    # Try to find the file
    possible_paths = [
        os.path.join(os.getcwd(), "..", "data", "quickstart_sample.pdf"),
        # os.path.join(os.getcwd(), "data", "simple.pdf"), # Fallback removed as per user request
    ]

    source_path = None
    for p in possible_paths:
        if os.path.exists(p):
            source_path = p
            break

    if not source_path:
        # Fallback to creating a dummy PDF if strictly needed for testing,
        # but better to raise error if data is missing.
        raise HTTPException(status_code=404, detail="Sample file (quickstart_sample.pdf) not found on server")

    # 2. Copy to Upload Dir
    file_id = str(uuid.uuid4())
    dest_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    try:
        shutil.copy(source_path, dest_path)
    except OSError as e:
        logger.error(f"Failed to copy sample file from {source_path} to {dest_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to copy sample file: {e}")

    # 3. Prepare Config
    metadata_content = """fields:
  - name: table_name
    description: Name of the table
    type: string
  - name: row_count
    description: Number of rows in the table
    type: integer
"""

    prompt_content = "Extract all tables from the provided document. Preserve the structure and cell contents."

    return {
        "file_id": file_id,
        "filename": os.path.basename(source_path),
        "metadata": metadata_content,
        "prompt": prompt_content,
    }


def run_extraction_task(pipeline_name: str, run_id: str, prompt: str, metadata_schema: dict, api_key: str = None):
    """Background task to run the extraction pipeline."""
    try:
        agent0.run_pipeline(pipeline_name, run_id, prompt, metadata_schema, api_key=api_key)
    except Exception as e:
        logger.error(f"Extraction failed for run_id {run_id} in pipeline {pipeline_name}: {e}")


@router.post("/extract")
async def extract_document(
    background_tasks: BackgroundTasks,
    file_id: str = Form(...),
    api_key: str = Form(...),
    metadata: str = Form(...),
    prompt: str = Form(...),
):
    """Trigger the document extraction process."""

    # Validate file existence
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Parse metadata YAML
    try:
        metadata_schema = yaml.safe_load(metadata) if metadata.strip() else None
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Metadata YAML: {e}")

    # Set Google API Key if provided
    # Passed explicitly to the extraction task to avoid global state issues
    # if api_key:
    #     os.environ["GOOGLE_API_KEY"] = api_key

    pipeline_name = "ui_extraction"

    # Initialize Pipeline using Agent0
    # This creates the directory structure and returns a run_id
    # We pass the temp pdf path, and it copies it to the pipeline input dir
    try:
        run_id, pipeline_metadata = agent0.create_pipeline(
            pipeline_name=pipeline_name,
            input_file_path=pdf_path,
            filename=f"doc_{file_id}.pdf",  # or original filename if we preserved it
        )
    except Exception as e:
        logger.error(f"Failed to create pipeline '{pipeline_name}' for file {pdf_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create pipeline: {e}")

    # Run in background
    # Run in background
    background_tasks.add_task(run_extraction_task, pipeline_name, run_id, prompt, metadata_schema, api_key=api_key)

    return {"job_id": run_id, "status": "pending", "pipeline_name": pipeline_name}


def get_directory_structure(root_dir):
    """
    Recursively builds a tree structure of the directory.
    """
    params = {"name": os.path.basename(root_dir), "path": root_dir, "type": "directory", "children": []}
    try:
        items = sorted(os.listdir(root_dir))
        for item in items:
            item_path = os.path.join(root_dir, item)
            if os.path.isdir(item_path):
                params["children"].append(get_directory_structure(item_path))
            else:
                params["children"].append({"name": item, "path": item_path, "type": "file"})
    except PermissionError:
        logger.error(f"Permission denied accessing directory: {root_dir}")

    return params


@router.get("/results/{job_id}")
async def get_results(job_id: str):
    pipeline_name = "ui_extraction"

    # Check current status from metadata.json
    try:
        metadata = agent0.fs_manager.load_metadata(pipeline_name, job_id)
    except Exception as e:
        logger.error(f"Error loading metadata for job {job_id}: {e}")
        raise HTTPException(status_code=404, detail="Job not found")

    if not metadata:
        raise HTTPException(status_code=404, detail="Job not found")

    run_path = agent0.fs_manager.get_pipeline_path(pipeline_name, job_id)

    # Construct response
    response_data = {
        "status": metadata.get("status", "UNKNOWN"),
        "error": metadata.get("error"),
        "metadata": metadata,
        "files": {"csv": [], "metadata": [], "system": get_directory_structure(run_path)},
    }

    # Find CSVs in output and aggregated
    output_dir = os.path.join(run_path, "output")
    if os.path.exists(output_dir):
        msg_files = [
            {"name": f, "path": os.path.join(output_dir, f)} for f in os.listdir(output_dir) if f.endswith(".csv")
        ]
        response_data["files"]["csv"] = msg_files

    # Find Metadata JSONs in output directory (per table metadata)
    if os.path.exists(output_dir):
        meta_files = [
            {"name": f, "path": os.path.join(output_dir, f)} for f in os.listdir(output_dir) if f.endswith(".json")
        ]
        response_data["files"]["metadata"] = meta_files

    return response_data


@router.get("/file")
async def get_file_content(path: str):
    """Serve file content."""
    # Define trusted roots (allow access strictly to sandboxed areas)
    trusted_roots = [os.path.abspath(UPLOAD_DIR), base_pipeline_path]

    try:
        # Resolve the absolute path to handle symlinks and ../ components
        formatted_path = os.path.abspath(path)
        real_path = os.path.realpath(formatted_path)
    except Exception as e:
        logger.error(f"Invalid path format for {path}: {e}")
        raise HTTPException(status_code=400, detail="Invalid path format")

    # Verify that the file is actually inside one of the trusted roots
    is_allowed = False
    for root in trusted_roots:
        # Check if trusted root is a prefix of the real path
        # os.path.commonpath throws if paths are on different drives on Windows, but fine here
        try:
            if os.path.commonpath([root, real_path]) == root:
                is_allowed = True
                break
        except ValueError:
            continue

    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access denied: Security violation")

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(real_path, filename=os.path.basename(real_path))


@router.get("/download-all/{job_id}")
async def download_all(job_id: str):
    """Zip the entire pipeline run directory and return it."""
    pipeline_name = "ui_extraction"
    try:
        # Validate job exists
        metadata = agent0.fs_manager.load_metadata(pipeline_name, job_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Job not found")

        run_path = agent0.fs_manager.get_pipeline_path(pipeline_name, job_id)

        run_path = agent0.fs_manager.get_pipeline_path(pipeline_name, job_id)

        # Create a secure temporary file for the zip archive
        # We use delete=False so we can serve it, but we should rely on BackgroundTasks to clean it up?
        # FileResponse can handle background tasks.

        # Using NamedTemporaryFile to get a secure path
        # The suffix must be .zip for make_archive to append nothing or we handle naming carefully
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.name.replace(".zip", "")
            # make_archive appends .zip automatically if format is zip
            # so we pass the path without extension if we want it to verify
            # But make_archive creates a NEW file.

            # A better way is:
            # create a temp dir, make archive inside it.

        # Let's use mkdtemp to create a secure directory, then make_archive inside it.
        tmp_dir = tempfile.mkdtemp()
        zip_base_name = os.path.join(tmp_dir, f"run_{job_id}")

        # shutil.make_archive(base_name, format, root_dir)
        # resulting file will be zip_base_name + .zip
        shutil.make_archive(zip_base_name, "zip", run_path)

        final_zip_path = zip_base_name + ".zip"

        # Define a cleanup function
        def cleanup():
            shutil.rmtree(tmp_dir, ignore_errors=True)

        bg_tasks = BackgroundTasks()
        bg_tasks.add_task(cleanup)

        return FileResponse(
            final_zip_path, filename=f"run_{job_id}.zip", media_type="application/zip", background=bg_tasks
        )

    except Exception as e:
        logger.error(f"Failed to create zip archive for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create zip: {e}")
