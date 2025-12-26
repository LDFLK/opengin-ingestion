# OpenGIN Ingestion Toolkit

OpenGIN Ingestion is a powerful document data extraction and tracing toolkit powered by Google Gemini 2.0. It provides a flexible agentic pipeline for extracting structured data, tables, and statistics from documents.

## Prerequisites

-   Python 3.10+
-   A Google Gemini API Key

## Installation

1.  **Create and activate a virtual environment**:
    ```bash
    mamba create -n doctracer python=3.10 -y
    mamba activate doctracer
    ```

2.  **Install the package in editable mode**:
    ```bash
    pip install -e .
    ```

3.  **Set Environment Variables**:
    Export your API key:
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```

## Command Line Interface (CLI)

The `opengin` CLI provides a unified tool to manage your ingestion pipelines and traces.

### Basic Commands

-   **Check Version/Help**
    ```bash
    opengin --help
    ```

### Tracer Commands

Manage your extraction pipelines, view runs, and clean up data.

-   **List All Runs**
    View all pipeline runs and their status.
    ```bash
    opengin tracer list-runs
    ```

-   **View Run Details**
    Get detailed information about a specific run, including generated output files.
    ```bash
    opengin tracer info <pipeline_name> <run_id>
    ```

-   **Delete a Run**
    Delete a specific run and its associated data (prompts for confirmation).
    ```bash
    opengin tracer delete <pipeline_name> <run_id>
    ```

-   **Delete an Entire Pipeline**
    Delete a pipeline and all its associated runs.
    ```bash
    opengin tracer delete-pipeline <pipeline_name>
    ```

-   **Clear All Data**
    Delete ALL pipelines and runs (use with caution).
    ```bash
    opengin tracer clear-all
    ```

## Using the Library

You can use `opengin` directly in your Python scripts to build custom extraction workflows.

### Examples

Check the `examples/` directory for ready-to-run scripts.

**Tabular Data Extraction:**
[examples/extragzt/README.md](examples/extragzt/README.md)

```bash
python examples/extragzt/tabular_extragzt_extract_sample.py path/to/document.pdf
```

## Running the API Server

You can also expose the functionality via a GraphQL API.

Start the FastAPI server:
```bash
uvicorn opengin.tracer.main:app --reload
```

Visit `http://localhost:8000/graphql` to access the GraphiQL interface.
