#!/usr/bin/env python3
"""
Doctracer Tabular Extraction Example

This example script demonstrates how to use the `opengin.tracer` library directly
to extract tabular data from a PDF file.

Usage:
    python tabular_extragzt_extract_sample.py <file_path> <prompt_file>
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


def perform_extraction(file_path: str, prompt_file: str, metadata_schema_path: str = None) -> None:
    """
    Runs the extraction pipeline using opengin.tracer library.

    Args:
        file_path (str): Path to the PDF file.
        prompt_file (str): Path to the text file containing the extraction prompt.
        metadata_schema_path (str): Path to the metadata schema YAML file.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    if not os.path.exists(prompt_file):
        logger.error(f"Prompt file not found: {prompt_file}")
        sys.exit(1)

    try:
        with open(prompt_file, "r") as f:
            extraction_prompt = f.read()
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
        agent0.run_pipeline(pipeline_name, run_id, extraction_prompt, metadata_schema=metadata_schema)

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

                metadata = table.get("metadata")
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
    parser.add_argument("prompt_file", help="Path to the prompt text file")
    parser.add_argument("--metadata-schema", help="Path to the metadata schema YAML file", default=None)

    args = parser.parse_args()
    perform_extraction(args.file_path, args.prompt_file, args.metadata_schema)


if __name__ == "__main__":
    main()
