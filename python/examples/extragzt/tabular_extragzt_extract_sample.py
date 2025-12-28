#!/usr/bin/env python3
"""
Doctracer Tabular Extraction Example

This example script demonstrates how to use the `opengin.tracer` library directly
to extract tabular data from a PDF file.

Usage:
    python tabular_extragzt_extract_sample.py <file_path>
"""

import argparse
import json
import logging
import os
import sys
import yaml

from opengin.tracer.agents.orchestrator import Agent0

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


EXTRACTION_PROMPT = """
    **Objective:** Extract all tables from the provided document.

    **Context:**
    - The document is a PDF containing tables with information about various ministers.
    - A single page may contain the continuation of one minister's table AND the start of a completely
      new minister's table.

    **Instructions:**
    1. **Identify Minister:** Locate the name of the minister associated with the table(s). **Crucial:** If a page
       transitions from one minister to another, you MUST extract them as **two separate tables**. Look for bold
       headings or structural breaks indicating a new minister.
    2. **Strict Row Alignment:** Each column generally has items with numbering (e.g., 1, 2, 3...). You must extract
       data such that one number refers to exactly ONE row across all columns.
       - If Column I has item "12" and Column II has no corresponding item, leave Column II **empty** for that row.
       - Do **not** compress the table; preserve the alignment based on the numbering.
       - Please extract the numbering given for each record as it is. Don't miss the numbers.
       - Ensure values per each column for each row are in order of the numbers associated with each record.
    3. **Metadata Collection:** Extract metadata for each table as per the provided metadata schema.
        - The metadata schema is provided in the `metadata_schema_path` argument.
        - The metadata schema is a YAML file containing a list of fields with their names, types, and descriptions.
        - The metadata schema is used to validate the extracted data.
        - Do not hallucinate fields, leave them empty if it is not clear in the source. 
        - All metadata fields must be there with or without values. 
        - Empty values must be left as "" (empty string).
    4. **Consolidate Data:** Ensure that all records belonging to the same minister are aggregated together.
    5. **Output Constraint:** Generate a separate, single output structure for each minister found. The goal is to
       produce specific CSV files for each minister containing ONLY their data. Make sure for each table there is
       a corresponding metadata file.
"""


def perform_extraction(file_path: str, metadata_schema_path: str = None) -> None:
    """
    Runs the extraction pipeline using opengin.tracer library.

    Args:
        file_path (str): Path to the PDF file.
        metadata_schema_path (str): Path to the metadata schema YAML file.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    try:
        # Initialize Agent0 Orchestrator
        agent0 = Agent0()
        pipeline_name = "example_extragzt_run"

        # Start Pipeline
        logger.info(f"Initializing pipeline for file: {file_path}")
        run_id, metadata = agent0.create_pipeline(pipeline_name, file_path, os.path.basename(file_path))

        # Load metadata schema if provided
        metadata_schema = None
        if metadata_schema_path:
            if os.path.exists(metadata_schema_path):
                with open(metadata_schema_path, "r") as f:
                    metadata_schema = yaml.safe_load(f)
                logger.info(f"Loaded metadata schema from: {metadata_schema_path}")
            else:
                logger.warning(f"Metadata schema file not found: {metadata_schema_path}")

        # Run Extraction
        logger.info(f"Running extraction with Run ID: {run_id}")
        agent0.run_pipeline(pipeline_name, run_id, EXTRACTION_PROMPT, metadata_schema=metadata_schema)

        # Retrieve Results
        fs_manager = agent0.fs_manager
        aggregated_path = fs_manager.get_aggregated_results_path(pipeline_name, run_id)

        if os.path.exists(aggregated_path):
            with open(aggregated_path, "r") as f:
                tables = json.load(f)

            print(f"\n--- Extracted {len(tables)} Tables ---")
            for table in tables:
                print(f"Table ID: {table.get('id', table.get('name', 'Unknown'))}")
                print(f"Name:     {table.get('name')}")
                print(f"Columns:  {table.get('columns')}")
                print(f"Rows:     {len(table.get('rows', []))} found")
                
                metadata = table.get('metadata')
                if metadata:
                    print("Metadata:")
                    print(json.dumps(metadata, indent=4))
                    
                print("-" * 40)
        else:
            logger.warning("Pipeline completed but no aggregated results found.")

    except Exception as e:
        logger.error(f"An error occurred during extraction: {e}")
        # If possible, print stack trace
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Doctracer Example: Tabular Data Extraction")
    parser.add_argument("file_path", help="Path to the PDF file to process")
    parser.add_argument("--metadata-schema", help="Path to the metadata schema YAML file", default=None)

    args = parser.parse_args()
    perform_extraction(args.file_path, args.metadata_schema)


if __name__ == "__main__":
    main()
