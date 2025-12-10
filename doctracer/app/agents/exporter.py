import os
import csv
import logging
import json

logger = logging.getLogger(__name__)

class Agent3:
    """
    The Exporter Agent.
    Responsible for converting aggregated tables into CSV files.
    """
    def __init__(self, fs_manager):
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str):
        logger.info(f"Agent 3: Starting export for '{pipeline_name}'")
        
        # Load aggregated results
        aggregated_path = os.path.join(self.fs_manager._get_pipeline_path(pipeline_name), "aggregated", "tables.json")
        if not os.path.exists(aggregated_path):
            logger.warning("No aggregated tables found to export.")
            return

        with open(aggregated_path, "r") as f:
            tables = json.load(f)
            
        output_dir = self.fs_manager.get_output_path(pipeline_name)
        
        for table in tables:
            table_name = table.get("name", "untitled").replace(" ", "_").lower()
            table_id = table.get("id", "unknown")
            filename = f"{table_name}_{table_id}.csv"
            file_path = os.path.join(output_dir, filename)
            
            columns = table.get("columns", [])
            rows = table.get("rows", [])
            
            try:
                with open(file_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    if columns:
                        writer.writerow(columns)
                    writer.writerows(rows)
                logger.info(f"Agent 3: Exported {filename}")
            except Exception as e:
                logger.error(f"Agent 3: Failed to export table {table_name} - {e}")

        logger.info(f"Agent 3: Completed export for '{pipeline_name}'")
