import os
import shutil
import uuid

import yaml
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from opengin.tracer.agents.orchestrator import Agent0

router = APIRouter()

# Initialize Orchestrator
# We use a fixed directory for the sandbox/pipelines
base_pipeline_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox", "pipelines"))
os.makedirs(base_pipeline_path, exist_ok=True)
agent0 = Agent0(base_path=base_pipeline_path)

# Temporary storage for upload before pipeline creation
UPLOAD_DIR = "/tmp/opengin_uploads"
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    return {"file_id": file_id, "filename": file.filename}


def run_extraction_task(pipeline_name: str, run_id: str, prompt: str, metadata_schema: dict, api_key: str = None):
    """Background task to run the extraction pipeline."""
    try:
        agent0.run_pipeline(pipeline_name, run_id, prompt, metadata_schema, api_key=api_key)
    except Exception as e:
        print(f"Extraction failed for {run_id}: {e}")


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
        pass
    return params


@router.get("/results/{job_id}")
async def get_results(job_id: str):
    pipeline_name = "ui_extraction"

    # Check current status from metadata.json
    try:
        metadata = agent0.fs_manager.load_metadata(pipeline_name, job_id)
    except Exception:
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
    trusted_roots = [
        os.path.abspath(UPLOAD_DIR),
        base_pipeline_path
    ]

    try:
        # Resolve the absolute path to handle symlinks and ../ components
        formatted_path = os.path.abspath(path)
        real_path = os.path.realpath(formatted_path)
    except Exception:
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

    # Determine media type suitable for browser viewing or text
    if path.endswith(".csv") or path.endswith(".txt") or path.endswith(".json") or path.endswith(".yml"):
        return FileResponse(real_path, filename=os.path.basename(real_path))
    
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

        # Create a zip file in temp
        zip_filename = f"run_{job_id}"
        zip_path = os.path.join("/tmp", zip_filename)

        shutil.make_archive(zip_path, "zip", run_path)

        final_zip_path = zip_path + ".zip"
        return FileResponse(final_zip_path, filename=f"{zip_filename}.zip", media_type="application/zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create zip: {e}")
