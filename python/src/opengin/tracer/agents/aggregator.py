import logging

logger = logging.getLogger(__name__)


class Agent2:
    """
    The Aggregator Agent (Agent 2).

    This agent is responsible for consolidating extraction results from multiple pages.
    It identifies tables that span across pages by matching their names (case-insensitive)
    and merges their rows into a single unified table structure.
    """

    def __init__(self, fs_manager):
        """
        Initialize the Aggregator Agent.

        Args:
            fs_manager (FileSystemManager): Instance for handling file operations.
        """
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str, run_id: str):
        """
        Executes the aggregation phase.

        1. Loads intermediate results from all processed pages.
        2. Groups tables by their normalized name (lowercase, stripped).
        3. Merges rows for tables with the same name.
        4. Saves the consolidated list of tables to the 'aggregated' directory.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
        """
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
                metadata = table.get("metadata", None)

                # Normalize Name
                norm_name = orig_name.strip().lower()

                # Find matching table by name AND schema
                key = norm_name
                counter = 1

                while key in aggregated_map:
                    existing_cols = aggregated_map[key]["columns"]
                    if columns == existing_cols:
                        break  # Found a match with same name and schema

                    # Schema mismatch, try next variant
                    logger.warning(
                        f"Schema mismatch for table '{orig_name}' (key: {key}). "
                        f"Expected {existing_cols}, got {columns}. Creating variant."
                    )
                    key = f"{norm_name}_{counter}"
                    counter += 1

                if key not in aggregated_map:
                    aggregated_map[key] = {
                        "name": orig_name if counter == 1 else f"{orig_name} ({counter-1})",
                        "columns": columns,
                        "rows": [],
                        "metadata": metadata,
                    }

                # Append rows
                if rows:
                    aggregated_map[key]["rows"].extend(rows)

        # Construct final aggregated list
        aggregated_tables = []
        for norm_name, data in aggregated_map.items():
            aggregated_tables.append(
                {
                    "name": data["name"],
                    "columns": data["columns"],
                    "rows": data["rows"],
                    "metadata": data.get("metadata"),
                }
            )

        # Save aggregated result
        self.fs_manager.save_aggregated_result(pipeline_name, run_id, aggregated_tables)
        msg = (
            f"Agent 2: Completed aggregation for '{pipeline_name}' run '{run_id}'. "
            f"Total tables: {len(aggregated_tables)}"
        )
        logger.info(msg)
