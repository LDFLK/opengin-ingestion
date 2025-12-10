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

    def run(self, pipeline_name: str):
        logger.info(f"Agent 2: Starting aggregation for '{pipeline_name}'")
        
        # Load all intermediate results
        pages_data = self.fs_manager.load_intermediate_results(pipeline_name)
        
        aggregated_tables = []
        
        for page_data in pages_data:
            page_num = page_data.get("page_num")
            tables = page_data.get("tables", [])
            
            for table in tables:
                self._merge_table(aggregated_tables, table, page_num)
                
        # Save aggregated result
        self.fs_manager.save_aggregated_result(pipeline_name, aggregated_tables)
        logger.info(f"Agent 2: Completed aggregation for '{pipeline_name}'. Total tables: {len(aggregated_tables)}")

    def _merge_table(self, aggregated_tables: List[Dict[str, Any]], new_table: Dict[str, Any], page_num: int):
        """
        Merges a new table into the existing list of aggregated tables.
        Matching logic:
        1. Same Name (case insensitive)
        2. Same Columns (exact match)
        """
        match_found = False
        
        for existing_table in aggregated_tables:
            # Check for column match (strong indicator)
            if self._columns_match(existing_table["columns"], new_table["columns"]):
                # Check for name match or just append if columns match strongly?
                # For now, let's require column match AND similar name OR just column match if unique?
                # Let's stick to strict column match + name match preference.
                if existing_table["name"].lower() == new_table["name"].lower():
                    # Exact match, append rows
                    existing_table["rows"].extend(new_table["rows"])
                    existing_table["pages"].append(page_num)
                    match_found = True
                    break
                elif self._columns_match(existing_table["columns"], new_table["columns"]):
                     # Columns match but name differs. 
                     # This might be "Page 1 Table" vs "Page 2 Table".
                     # Let's assume they are the same if columns are identical.
                     existing_table["rows"].extend(new_table["rows"])
                     existing_table["pages"].append(page_num)
                     match_found = True
                     break
        
        if not match_found:
            # Add as new table
            new_entry = {
                "id": new_table["id"], # Keep original ID of first occurrence
                "name": new_table["name"],
                "columns": new_table["columns"],
                "rows": new_table["rows"],
                "pages": [page_num]
            }
            aggregated_tables.append(new_entry)

    def _columns_match(self, cols1: List[str], cols2: List[str]) -> bool:
        return [c.strip().lower() for c in cols1] == [c.strip().lower() for c in cols2]
