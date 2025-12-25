import logging

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
            tables = page_data.get("tables", [])

            for table in tables:
                orig_name = table.get("name", "Untitled")
                columns = table.get("columns", [])
                rows = table.get("rows", [])

                # Normalize Name
                norm_name = orig_name.strip().lower()

                if norm_name not in aggregated_map:
                    aggregated_map[norm_name] = {
                        "name": orig_name,
                        "columns": columns,
                        "rows": [],
                    }

                # Append rows
                if rows:
                    aggregated_map[norm_name]["rows"].extend(rows)

        # Construct final aggregated list
        aggregated_tables = []
        for norm_name, data in aggregated_map.items():
            aggregated_tables.append({"name": data["name"], "columns": data["columns"], "rows": data["rows"]})

        # Save aggregated result
        self.fs_manager.save_aggregated_result(pipeline_name, run_id, aggregated_tables)
        msg = (
            f"Agent 2: Completed aggregation for '{pipeline_name}' run '{run_id}'. "
            f"Total tables: {len(aggregated_tables)}"
        )
        logger.info(msg)
