---
sidebar_position: 1
---

# Extracting Tabular Data

Values: **Python Script**, **Tabular Data**, **Pipeline**

This tutorial guides you through using the `tabular_extragzt_extract_sample.py` example script. This script demonstrates how to utilize the `opengin.tracer` library to automate the extraction of tabular data from PDF documents.

## Overview

The example script is located at `python/examples/extragzt/tabular_extragzt_extract_sample.py`.

It performs the following high-level actions:
1.  **Initializes** a pipeline with the Orchestrator (Agent 0).
2.  **Scans** and extracts data from each page using the Scanner (Agent 1).
3.  **Aggregates** the results using the Aggregator (Agent 2).
4.  **Exports** the data using the Exporter (Agent 3).

## The Code Explained

Here's a breakdown of the key components in the script.

### 1. Setup and Initialization

The script starts by initializing the `Agent0` orchestrator. This agent manages the entire lifecycle of the pipeline.

```python
from opengin.tracer.agents.orchestrator import Agent0

def perform_extraction(file_path: str) -> None:
    # Initialize Agent0 Orchestrator
    agent0 = Agent0()
    pipeline_name = "example_extragzt_run"
    
    # Start Pipeline
    # creates the directory structure and generates a run_id
    run_id, metadata = agent0.create_pipeline(
        pipeline_name,
        file_path,
        os.path.basename(file_path)
    )
```

### 2. Defining the Extraction Prompt

The core logic of *what* to extract is defined in the `EXTRACTION_PROMPT`. This prompt is sent to the GenAI model (Gemini).

```python
EXTRACTION_PROMPT = """
    **Objective:** Extract all tables from the provided document.
    
    **Instructions:**
    1. **Identify Minister:** Locate the name of the minister...
    2. **Strict Row Alignment:** Each column generally has items...
    ...
"""
```

### 3. Running the Pipeline

The actual processing is triggered by a single call to `run_pipeline`. This method coordinates the hand-off between Agent 1, Agent 2, and Agent 3.

```python
    # Run Extraction
    agent0.run_pipeline(pipeline_name, run_id, EXTRACTION_PROMPT)
```

### 4. Retrieving Results

Once the pipeline completes, the script reads the aggregated results from the file system.

```python
    # Retrieve Results
    fs_manager = agent0.fs_manager
    aggregated_path = fs_manager.get_aggregated_results_path(pipeline_name, run_id)

    with open(aggregated_path, "r") as f:
        tables = json.load(f)
```

## Running the Example

To run the example, use the following command from the root of the project:

```bash
python python/examples/extragzt/tabular_extragzt_extract_sample.py <path_to_pdf>
```

### Example Output

When you run the script, you will see logs indicating the progress of each agent:

```text
INFO - Agent 0: Starting pipeline 'example_extragzt_run' run 'uuid...'
INFO - Agent 1: Starting scanning...
INFO - Agent 1: Processing page 1/5
...
INFO - Agent 2: Triggering Aggregation...
INFO - Agent 3: Triggering Export...
```

Finally, the script prints a summary of the extracted tables:

```text
--- Extracted 3 Tables ---
Table ID: minister_table_1
Name:     Minister of Finance
Columns:  ['Date', 'Description', 'Amount']
Rows:     12 found
----------------------------------------
```

## Extraction with Metadata

You can also extract metadata associated with each table by providing a metadata schema.

### 1. Define the Schema

Create a YAML file (e.g., `metadata.yml`) defining the fields you want to extract:

```yaml
fields:
  - name: category
    description: The category of the data in the table
    type: string
  - name: confidence
    description: Confidence score (0-1) of the extraction
    type: float
```

### 2. Run with Schema

Pass the `--metadata-schema` argument to the script:

```bash
python python/examples/extragzt/tabular_extragzt_extract_sample.py <path_to_pdf> --metadata-schema python/examples/extragzt/metadata.yml
```

The extracted metadata will be printed to the console and saved as a JSON file (e.g., `tablename_metadata.json`) alongside the CSV output.

## Generated Files

For every run, the tracer creates a dedicated directory structure in `pipelines/`:

-   `pipelines/<pipeline_name>/<run_id>/input/`: Contains the original PDF and split pages.
-   `pipelines/<pipeline_name>/<run_id>/intermediate/`: Contains JSON files for each individual page extraction.
-   `pipelines/<pipeline_name>/<run_id>/aggregated/`: Contains the consolidated `tables.json`.
-   `pipelines/<pipeline_name>/<run_id>/output/`: Contains the final exported files (e.g., CSVs).
