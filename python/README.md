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

-   **Run a Pipeline**
    Start an extraction job for a file or URL.
    ```bash
    # Local file
    opengin tracer run ./data/doc.pdf --prompt "Extract all tables."

    # URL
    opengin tracer run https://example.com/report.pdf
    
    # Using a prompt file
    opengin tracer run ./data/doc.pdf --prompt ./prompts/finance.txt

    # With Metadata Schema
    opengin tracer run ./data/doc.pdf --metadata-schema ./schemas/metadata.yml
    ```

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

python examples/extragzt/tabular_extragzt_extract_sample.py path/to/document.pdf
```

**Metadata Extraction:**
You can enforce specific metadata extraction by providing a schema YAML file.

### Metadata Schema Specification

The metadata schema is a YAML file used to define the fields that should be extracted for each table.

**Structure:**
The root of the YAML file must contain a `fields` list. Each item in the list represents a metadata field to be extracted.

```yaml
fields:
  - name: <field_name>        # Required: The key for the metadata field
    description: <text>       # Optional: Description to guide the extraction
    type: <data_type>         # Optional: Expected type (string, integer, float, boolean)
```

**Example:**
```yaml
fields:
  - name: author
    description: The author of the document
    type: string
  - name: created_date
    description: The creation date of the document
    type: string
```

**Run Command:**
```bash
python examples/extragzt/tabular_extragzt_extract_sample.py doc.pdf --metadata-schema examples/extragzt/metadata.yml
```

## Running the API Server

You can also expose the functionality via a GraphQL API.

Start the FastAPI server:
```bash
uvicorn opengin.tracer.main:app --reload
```

Visit `http://localhost:8000/graphql` to access the GraphiQL interface.
