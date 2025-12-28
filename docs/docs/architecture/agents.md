---
sidebar_position: 2
---

# Agents

This section details the responsibilities and logic of each agent in the OpenGIN Tracer system.

## Agent 0: Orchestrator

**Role**: Lifecycle Management & Coordination

The Orchestrator is the entry point for any pipeline run. Its duties include:
- Generating unique `run_id`s for tracking.
- Creating the directory structure for the pipeline (input, intermediate, output folders).
- invoking the subsequent agents in the correct order.
- Handling global error states and metadata updates.

## Agent 1: Scanner

**Role**: Document Processing & Extraction

The Scanner extracts raw data from the source document.
- **Input**: A raw PDF file.
- **Process**:
    1.  Splits the PDF into single-page PDF files using `pypdf`.
    2.  Iterates through each page.
    3.  Sends the page to **Google Gemini 2.0 Flash** (configurable via environment variable) with a prompt to "Extract all tables".
    4.  **Metadata (Optional)**: If a schema is provided, it also instructs the model to extract specific metadata fields for each table.
    5.  Parses the JSON response from Gemini.
- **Output**: A collection of JSON files in the `intermediate/` directory, one per page.

## Agent 2: Aggregator

**Role**: Data Consolidation

The Aggregator combines the fragmented page-level data.
- **Input**: The collection of `intermediate/page_*.json` files.
- **Process**:
    - Reads all intermediate files in order.
    - Aggregates tables that might span multiple pages (future capability) or simply collects all tables into a master list.
    - **Metadata Handling**: Preserves table-level metadata during aggregation.
- **Output**: A single `aggregated/tables.json` file containing all extracted data.

## Agent 3: Exporter

**Role**: Final Output Generation

The Exporter formats the data for consumption.
- **Input**: The `aggregated/tables.json` file.
- **Process**:
    - Transforms the hierarchical JSON structure into a flat format suitable for analysis or database insertion.
    - Uses `csv` module to generate CSV files for each table.
    - Exports associated metadata as JSON files if present.
- **Output**: Final files in the `output/` directory (e.g., `table_name.csv`, `table_name_metadata.json`).
