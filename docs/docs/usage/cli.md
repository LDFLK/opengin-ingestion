---
sidebar_position: 1
---

# CLI Usage

OpenGIN Tracer provides a Command Line Interface (CLI) to interact with the pipeline.

## Installation

Ensure you have the package installed (preferably in a virtual environment):

```bash
pip install -e .
```

## Running a Trace

To extract data from a PDF file, use the `opengin tracer run` command.

```bash
opengin tracer run <path_to_pdf> --name <pipeline_name>
```

### Arguments

- `path_to_pdf`: Absolute or relative path to the source PDF file.
- `--name`: A human-readable name for this pipeline run (e.g., "financial_report_2024").

### Example

```bash
opengin tracer run ./data/sample_invoice.pdf --name output_pipeline
```

## Output

After execution, the results can be found in the `pipelines/<pipeline_name>/<run_id>/output/` directory.

The console output will display the `run_id` for your reference.
