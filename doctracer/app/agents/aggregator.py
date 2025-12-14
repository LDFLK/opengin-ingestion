import logging
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Agent2:
    """
    The Aggregator Agent.
    Responsible for merging extractions from multiple pages into unified tables.
    """
    def __init__(self, fs_manager):
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str, run_id: str):
        logger.info(f"Agent 2: Starting aggregation for '{pipeline_name}' run '{run_id}'")
        
        # Load all intermediate results
        pages_data = self.fs_manager.load_intermediate_results(pipeline_name, run_id)
        
        # Dictionary to hold aggregated tables: normalized_name -> {name, csv_content (list of strings)}
        aggregated_map = {}
        
        for page_data in pages_data:
            page_num = page_data.get("page_num")
            tables = page_data.get("tables", [])
            
            for table in tables:
                orig_name = table.get("name", "Untitled")
                csv_content = table.get("csv", "")
                
                # Normalize Name
                norm_name = orig_name.strip().lower()
                
                if norm_name not in aggregated_map:
                    aggregated_map[norm_name] = {
                        "name": orig_name,
                        "csv_parts": []
                    }
                
                # For the first part, keep everything.
                # For subsequent parts, remove the first line (header) if it exists and looks like a header
                if len(aggregated_map[norm_name]["csv_parts"]) == 0:
                    aggregated_map[norm_name]["csv_parts"].append(csv_content)
                else:
                    # Simple heuristic: Split lines and drop the first one
                    lines = csv_content.splitlines(keepends=True)
                    if len(lines) > 1:
                        # Append from 2nd line onwards
                        aggregated_map[norm_name]["csv_parts"].append("".join(lines[1:]))
                    elif len(lines) == 1:
                         # Ensure we don't just paste headers repeatedly if there are no rows
                         # If it's just a header and we already have parts, skip
                         pass
        
        # Construct final aggregated list
        aggregated_tables = []
        for norm_name, data in aggregated_map.items():
            full_csv = "".join(data["csv_parts"])
            aggregated_tables.append({
                "name": data["name"],
                "csv": full_csv
            })
                
        # Save aggregated result
        self.fs_manager.save_aggregated_result(pipeline_name, run_id, aggregated_tables)
        logger.info(f"Agent 2: Completed aggregation for '{pipeline_name}' run '{run_id}'. Total tables: {len(aggregated_tables)}")
