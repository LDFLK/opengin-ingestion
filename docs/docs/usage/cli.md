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

To extract data from a PDF file, use the `opengin tracer run` command. This command supports both local files and URLs.

```bash
opengin tracer run <INPUT_SOURCE> [OPTIONS]
```

### Arguments

- `INPUT_SOURCE`: Absolute/relative path to a local PDF file OR a URL (starting with `http://` or `https://`).

### Options

- `--name`: A human-readable name for this pipeline run (e.g., "financial_report_2024"). Defaults to `run_<timestamp>`.
- `--prompt`: The extraction prompt text OR a path to a text file containing the prompt. Defaults to "Extract all tables.".

### Examples

**1. Basic Usage (Local File):**
```bash
opengin tracer run ./data/sample_invoice.pdf --name output_pipeline
```

**2. Using a Remote URL:**
The CLI will automatically download the file to a temporary location, process it, and clean it up.
```bash
opengin tracer run https://raw.githubusercontent.com/LDFLK/opengin-ingestion/main/data/quickstart_sample.pdf --name quickstart-sample
```

**3. Using a Prompt File:**
For complex instructions, save your prompt in a text file.
```bash
opengin tracer run ./data/invoice.pdf --prompt ./prompts/invoice_extraction.txt
```

## Output

After execution, the results can be found in the `pipelines/<pipeline_name>/<run_id>/output/` directory.

The console output will display the `run_id` for your reference.
