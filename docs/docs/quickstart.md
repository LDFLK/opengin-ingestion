---
sidebar_position: 2
---

# Quick Start

Get up and running with OpenGIN Tracer in minutes.

## Installation

To install the latest version of OpenGIN Tracer, use pip:

```bash
pip install opengin-ingestion
```

Or install from source if you have the repository cloned:

```bash
pip install -e .
```

## Hands-on Example

:::danger Important: Gemini API Key Required
You must set the `GOOGLE_API_KEY` environment variable for the tracer to work.
Without it, the system will run in **Mock Mode**, returning static dummy data for every page (which will look like duplicate tables).

```bash
export GOOGLE_API_KEY="your_api_key_here"
```
:::

In this guide, we will use a generated sample PDF to demonstrate how to extract tables using the Python API.

### 1. The Scenario

We have a 5-page PDF file (`data/quickstart_sample.pdf`) where each page contains a table with a title. 

-   **Goal**: Extract the table from each page into a separate CSV file.
-   **Output**: 5 CSV files (or JSONs) containing the structure data.

*(If you don't have the sample PDF, you can generate it running `python scripts/generate_sample_pdf.py`)*

### 2. Create Metadata Schema (Optional)

Create a file named `metadata.yml` to define what extra information you want to extract about the data:

```yaml
fields:
  - name: table_category
    description: The category of the table (e.g., Financial, Inventory, Staff)
    type: string
  - name: confidence_score
    description: A score from 0 to 1 indicating confidence in extraction
    type: float
  - name: row_count
    description: Number of rows in the table
    type: integer
  - name: column_count
    description: Number of columns in the table
    type: integer


### 3. Create the Extraction Script

Create a file named `quickstart_extract.py` with the following content:

```python
import os
import yaml
from opengin.tracer.agents.orchestrator import Agent0

# Define what we want to extract
EXTRACTION_PROMPT = """
    **Objective:** Extract the table from the current page.
    
    **Instructions:**
    1. **Identify**: Locate the table and its title/heading.
    2. **Naming**: Use the table title as the table name. Convert it to snake_case.
    3. **Extract**: Extract all rows and columns accurately.
    4. **Metadata**: Extract the metadata as defined in the schema, one metadata per table.
    5. **Separate**: If multiple tables exist, extract them as separate entities, each with its own name.
"""

def main():
    # 1. Setup paths
    input_pdf = "data/quickstart_sample.pdf"
    pipeline_name = "quickstart_run"
    metadata_file = "metadata.yml"
    
    if not os.path.exists(input_pdf):
        print(f"Error: {input_pdf} not found. Please run scripts/generate_sample_pdf.py first.")
        return

    # 2. Load Metadata Schema
    metadata_schema = None
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata_schema = yaml.safe_load(f)
        print("Loaded metadata schema.")

    # 3. Initialize the Orchestrator
    agent0 = Agent0()
    
    print(f"Initializing pipeline for: {input_pdf}")
    run_id, metadata = agent0.create_pipeline(
        pipeline_name,
        input_pdf,
        os.path.basename(input_pdf)
    )

    # 4. Run the Pipeline
    print(f"Running extraction (Run ID: {run_id})...")
    agent0.run_pipeline(pipeline_name, run_id, EXTRACTION_PROMPT, metadata_schema=metadata_schema)
    
    # 5. Success Message
    print(f"Extraction complete! Check results in: pipelines/{pipeline_name}/{run_id}/output/")

if __name__ == "__main__":
    main()
```

### 4. Run the Script

Execute the script in your terminal:

```bash
python quickstart_extract.py
```

### 4. Check Results with CLI

OpenGIN comes with a CLI to manage and inspect your pipeline runs.

1.  **List Runs**: See all your pipeline executions.
    ```bash
    opengin tracer list-runs
    ```
    *Output:*
    ```text
    +----------------+--------------------------------------+-----------+-------+
    | Pipeline       | Run ID                               | Status    | Pages |
    +================+======================================+===========+=======+
    | quickstart_run | 9ce866d1-58f0-46e1-a369-0f8ca26e8c54 | COMPLETED |     5 |
    +----------------+--------------------------------------+-----------+-------+
    ```

2.  **Inspect Run**: Get detailed information about a specific run using its name and ID.
    ```bash
    opengin tracer info quickstart_run <YOUR_RUN_ID>
    ```
    *Output:*
    ```json
    {
      "pipeline_name": "quickstart_run",
      "run_id": "9ce866d1-58f0-46e1-a369-0f8ca26e8c54",
      "created_at": "2025-12-26 07:22:13.297861",
      "status": "COMPLETED",
      "page_count": 5,
      "current_stage": "EXPORTING",
      "input_file": "pipelines/quickstart_run/9ce866d1-58f0-46e1-a369-0f8ca26e8c54/input/quickstart_sample.pdf"
    }

    Output Files:
     - sample_data_table.csv
     - sample_data_table_metadata.json
    ```

3.  **View Data**: Navigate to the output directory shown in the info command to see your CSVs and JSONs.
    ```bash
    ls pipelines/quickstart_run/<YOUR_RUN_ID>/output/
    ```

## Next Steps

-   Explore the [Architecture](architecture/overview) to understand how the orchestrator works.
-   Check out the [Tutorials](tutorial/extragzt) for more complex examples.
