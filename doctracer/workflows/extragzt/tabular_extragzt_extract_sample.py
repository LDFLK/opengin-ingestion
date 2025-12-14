#!/usr/bin/env python3
"""
Doctracer Tabular Extraction Workflow Client

This CLI application uploads a PDF file to the Doctracer GraphQL API to extract
tabular data based on a predefined prompt for minister schedules.

Usage:
    python tabular_extragzt_extract_sample.py <file_path> [--url <api_url>]
"""

import sys
import json
import argparse
import logging
import requests
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_URL = "http://localhost:8000/graphql"

EXTRACTION_PROMPT = """
    **Objective:** Extract all tables from the provided document.

    **Context:**
    - The document is a PDF containing tables with information about various ministers.
    - A single page may contain the continuation of one minister's table AND the start of a completely new minister's table.

    **Instructions:**
    1. **Identify Minister:** Locate the name of the minister associated with the table(s). **Crucial:** If a page transitions from one minister to another, you MUST extract them as **two separate tables**. Look for bold headings or structural breaks indicating a new minister.
    2. **Strict Row Alignment:** Each column generally has items with numbering (e.g., 1, 2, 3...). You must extract data such that one number refers to exactly ONE row across all columns. 
       - If Column I has item "12" and Column II has no corresponding item, leave Column II **empty** for that row. 
       - Do **not** compress the table; preserve the alignment based on the numbering.
    3. **Consolidate Data:** Ensure that all records belonging to the same minister are aggregated together.
    4. **Output Constraint:** Generate a separate, single output structure for each minister found. The goal is to produce specific CSV files for each minister containing ONLY their data.
"""

GRAPHQL_QUERY = """
    mutation UploadAndExtract($file: Upload!, $prompt: String!) {
      extractData(file: $file, prompt: $prompt) {
        message
        rawResponse
        tables {
          id
          name
          columns
          rows
        }
      }
    }
"""

def perform_extraction(file_path: str, url: str) -> None:
    """
    Uploads the file to the GraphQL API and prints the extracted results.

    Args:
        file_path (str): Path to the PDF file.
        url (str): GraphQL API endpoint URL.
    """
    logger.info(f"Target API URL: {url}")
    logger.info(f"Uploading file: {file_path}")

    # Prepare Payload
    operations_payload = {
        "query": GRAPHQL_QUERY,
        "variables": {
            "file": None,  # Mapped via 'map' in multipart
            "prompt": EXTRACTION_PROMPT
        }
    }

    multipart_data = {
        "operations": (None, json.dumps(operations_payload), "application/json"),
        "map": (None, json.dumps({"0": ["variables.file"]}), "application/json"),
    }

    try:
        # Open file in binary mode
        with open(file_path, "rb") as f:
            files_payload = {
                **multipart_data,
                "0": (file_path, f, "application/pdf")
            }
            
            logger.info("Sending request to GraphQL API...")
            response = requests.post(url, files=files_payload)
            response.raise_for_status()

            data = response.json()
            
            if "errors" in data:
                logger.error("GraphQL Errors returned:")
                print(json.dumps(data["errors"], indent=2))
                sys.exit(1)

            result = data.get("data", {}).get("extractData", {})
            message = result.get("message", "")
            tables = result.get("tables", [])

            logger.info(f"Extraction successful: {message}")
            print(f"\n--- Extracted {len(tables)} Tables ---")
            
            for table in tables:
                print(f"Table ID: {table.get('id')}")
                print(f"Name:     {table.get('name')}")
                print(f"Columns:  {table.get('columns')}")
                print(f"Rows:     {len(table.get('rows', []))} found")
                print("-" * 40)

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        if e.response is not None:
             logger.error(f"Server response: {e.response.text}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response from server.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Doctracer Workflow: Tabular Data Extraction Sample"
    )
    parser.add_argument(
        "file_path", 
        help="Path to the PDF file to process"
    )
    parser.add_argument(
        "--url", 
        default=DEFAULT_URL, 
        help=f"GraphQL API URL (default: {DEFAULT_URL})"
    )

    args = parser.parse_args()
    perform_extraction(args.file_path, args.url)

if __name__ == "__main__":
    main()
