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

from opengin.tracer.agents.orchestrator import Agent0

# Ensure src is in the python path if running from source without installation
# This logic is just for convenience in this example
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))


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
    3. **Consolidate Data:** Ensure that all records belonging to the same minister are aggregated together.
    4. **Output Constraint:** Generate a separate, single output structure for each minister found. The goal is to
       produce specific CSV files for each minister containing ONLY their data.
"""


def perform_extraction(file_path: str) -> None:
    """
    Runs the extraction pipeline using opengin.tracer library.

    Args:
        file_path (str): Path to the PDF file.
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

        # Run Extraction
        logger.info(f"Running extraction with Run ID: {run_id}")
        agent0.run_pipeline(pipeline_name, run_id, EXTRACTION_PROMPT)

        # Retrieve Results
        fs_manager = agent0.fs_manager
        aggregated_path = os.path.join(
            fs_manager._get_pipeline_path(pipeline_name, run_id),
            "aggregated",
            "tables.json",
        )

        if os.path.exists(aggregated_path):
            with open(aggregated_path, "r") as f:
                tables = json.load(f)

            print(f"\n--- Extracted {len(tables)} Tables ---")
            for table in tables:
                print(f"Table ID: {table.get('id', table.get('name', 'Unknown'))}")
                print(f"Name:     {table.get('name')}")
                print(f"Columns:  {table.get('columns')}")
                print(f"Rows:     {len(table.get('rows', []))} found")
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

    args = parser.parse_args()
    perform_extraction(args.file_path)


if __name__ == "__main__":
    main()
