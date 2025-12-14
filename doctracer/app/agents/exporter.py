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

    def run(self, pipeline_name: str, run_id: str):
        logger.info(f"Agent 3: Starting export for '{pipeline_name}' run '{run_id}'")
        
        # Load aggregated results
        aggregated_path = os.path.join(self.fs_manager._get_pipeline_path(pipeline_name, run_id), "aggregated", "tables.json")
        if not os.path.exists(aggregated_path):
            logger.warning("No aggregated tables found to export.")
            return

        with open(aggregated_path, "r") as f:
            tables = json.load(f)
            
        output_dir = self.fs_manager.get_output_path(pipeline_name, run_id)
        
        for table in tables:
            table_name = table.get("name", "untitled").replace(" ", "_").lower()
            # Clean filename
            table_name = "".join(c for c in table_name if c.isalnum() or c in ('_', '-'))
            filename = f"{table_name}.csv"
            filepath = os.path.join(output_dir, filename)
            
            csv_content = table.get("csv", "")
            
            with open(filepath, "w") as f:
                f.write(csv_content)
                
            logger.info(f"Agent 3: Exported {filename}")
        
        logger.info(f"Agent 3: Completed export for '{pipeline_name}'")
