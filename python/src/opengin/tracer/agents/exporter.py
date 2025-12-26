import csv
import io
import json
import logging
import os

logger = logging.getLogger(__name__)


class Agent3:
    """
    The Exporter Agent (Agent 3).

    This agent is responsible for the final output generation.
    It takes the aggregated table data (from Agent 2) and converts each table
    into a separate CSV file in the 'output' directory.
    """

    def __init__(self, fs_manager):
        """
        Initialize the Exporter Agent.

        Args:
            fs_manager (FileSystemManager): Instance for handling file operations.
        """
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str, run_id: str):
        """
        Executes the export phase.

        1. Loads the aggregated tables from the 'aggregated' directory.
        2. Iterates through each table.
        3. Sanitizes the table name to create a valid filename.
        4. Writes the table content (headers and rows) to a CSV file.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
        """
        logger.info(f"Agent 3: Starting export for '{pipeline_name}' run '{run_id}'")

        # Load aggregated results
        aggregated_path = self.fs_manager.get_aggregated_results_path(pipeline_name, run_id)
        if not os.path.exists(aggregated_path):
            logger.warning("No aggregated tables found to export.")
            return

        with open(aggregated_path, "r") as f:
            tables = json.load(f)

        output_dir = self.fs_manager.get_output_path(pipeline_name, run_id)

        for table in tables:
            table_name = table.get("name", "untitled").replace(" ", "_").lower()
            # Clean filename
            table_name = "".join(c for c in table_name if c.isalnum() or c in ("_", "-"))

            # Ensure unique filename
            base_filename = table_name
            extension = ".csv"
            counter = 1
            filename = f"{base_filename}{extension}"
            filepath = os.path.join(output_dir, filename)

            while os.path.exists(filepath):
                filename = f"{base_filename}_{counter}{extension}"
                filepath = os.path.join(output_dir, filename)
                counter += 1

            columns = table.get("columns", [])
            rows = table.get("rows", [])

            output = io.StringIO()
            writer = csv.writer(output)

            if columns:
                writer.writerow(columns)

            if rows:
                writer.writerows(rows)

            with open(filepath, "w") as f:
                f.write(output.getvalue())

            logger.info(f"Agent 3: Exported {filename}")

        # Update metadata to status COMPLETED
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        metadata["status"] = "COMPLETED"
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        logger.info(f"Agent 3: Completed export for '{pipeline_name}' run '{run_id}'")
