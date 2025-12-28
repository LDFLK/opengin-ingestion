import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List

from opengin.tracer.agents.aggregator import Agent2
from opengin.tracer.agents.exporter import Agent3
from opengin.tracer.agents.scanner import Agent1

logger = logging.getLogger(__name__)


class FileSystemManager:
    """
    Manages the file system structure for the pipeline.

    This class handles the creation, organization, and access of files and directories
    generated during the data extraction pipeline. It ensures a consistent structure
    for each pipeline run.

    Structure:
    /pipelines/
      /{pipeline_name}/
        /{run_id}/
            metadata.json       # Stores run status, timestamps, and config
            /input/             # Raw input files (e.g., PDFs)
            /intermediate/      # Per-page extraction results (JSON)
            /aggregated/        # Combined results before final export
            /output/            # Final exported files (CSV, etc.)
    """

    def __init__(self, base_path: str = "pipelines"):
        """
        Initialize the FileSystemManager.

        Args:
            base_path (str): The root directory where all pipelines will be stored.
                             Defaults to "pipelines".
        """
        self.base_path = base_path

    def get_pipeline_path(self, pipeline_name: str, run_id: str) -> str:
        """
        Constructs the absolute path for a specific pipeline run.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            str: The full path to the run directory.
        """
        return os.path.join(self.base_path, pipeline_name, run_id)

    def initialize_pipeline(self, pipeline_name: str, run_id: str):
        """
        Creates the directory structure for a new pipeline run.

        This method creates the necessary subdirectories (input, intermediate,
        aggregated, output) and initializes the metadata file.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
        """
        path = self.get_pipeline_path(pipeline_name, run_id)

        # Create directories
        os.makedirs(os.path.join(path, "input"), exist_ok=True)
        os.makedirs(os.path.join(path, "intermediate"), exist_ok=True)
        os.makedirs(os.path.join(path, "aggregated"), exist_ok=True)
        os.makedirs(os.path.join(path, "output"), exist_ok=True)

        # Initialize metadata
        metadata = {
            "pipeline_name": pipeline_name,
            "run_id": run_id,
            "created_at": str(datetime.now()),
            "status": "INITIALIZED",
            "page_count": 0,
            "current_stage": "SETUP",
        }
        self.save_metadata(pipeline_name, run_id, metadata)
        logger.info(f"Pipeline '{pipeline_name}' run '{run_id}' initialized at {path}")

    def save_metadata(self, pipeline_name: str, run_id: str, metadata: Dict[str, Any]):
        """
        Saves metadata to the metadata.json file.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            metadata (Dict[str, Any]): The metadata dictionary to save.
        """
        path = os.path.join(self.get_pipeline_path(pipeline_name, run_id), "metadata.json")
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def load_metadata(self, pipeline_name: str, run_id: str) -> Dict[str, Any]:
        """
        Loads metadata from the metadata.json file.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            Dict[str, Any]: The loaded metadata, or an empty dict if file not found.
        """
        path = os.path.join(self.get_pipeline_path(pipeline_name, run_id), "metadata.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def save_input_file(self, pipeline_name: str, run_id: str, file_path: str, filename: str) -> str:
        """
        Copies the input file to the pipeline's input directory.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            file_path (str): The source path of the input file.
            filename (str): The destination filename.

        Returns:
            str: The path to the saved input file within the pipeline structure.
        """
        filename = os.path.basename(filename)
        dest_path = os.path.join(self.get_pipeline_path(pipeline_name, run_id), "input", filename)
        shutil.copy(file_path, dest_path)
        return dest_path

    def save_intermediate_result(self, pipeline_name: str, run_id: str, page_num: int, data: Any):
        """
        Saves extraction results for a specific page.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            page_num (int): The page number associated with the data.
            data (Any): The extraction result data (usually a dictionary).
        """
        path = os.path.join(
            self.get_pipeline_path(pipeline_name, run_id),
            "intermediate",
            f"page_{page_num}.json",
        )
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load_intermediate_results(self, pipeline_name: str, run_id: str) -> List[Any]:
        """
        Loads all intermediate page results for a pipeline run.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            List[Any]: A list of data from all page files, sorted by page number.
        """
        intermediate_path = os.path.join(self.get_pipeline_path(pipeline_name, run_id), "intermediate")
        results = []
        if not os.path.exists(intermediate_path):
            return results

        # Sort by page number to ensure order
        files = sorted(
            [f for f in os.listdir(intermediate_path) if f.startswith("page_") and f.endswith(".json")],
            key=lambda x: int(x.split("_")[1].split(".")[0]),
        )

        for filename in files:
            with open(os.path.join(intermediate_path, filename), "r") as f:
                results.append(json.load(f))
        return results

    def save_aggregated_result(self, pipeline_name: str, run_id: str, data: Any):
        """
        Saves the aggregated results to the 'aggregated' directory.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            data (Any): The combined data from all pages.
        """
        path = os.path.join(self.get_pipeline_path(pipeline_name, run_id), "aggregated", "tables.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_output_path(self, pipeline_name: str, run_id: str) -> str:
        """
        Returns the path to the output directory.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            str: The full path to the output directory.
        """
        return os.path.join(self.get_pipeline_path(pipeline_name, run_id), "output")

    def get_input_pages_dir(self, pipeline_name: str, run_id: str) -> str:
        """
        Returns the path to the directory where split PDF pages are stored.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            str: The full path to the input/pages directory.
        """
        return os.path.join(self.get_pipeline_path(pipeline_name, run_id), "input", "pages")

    def get_aggregated_results_path(self, pipeline_name: str, run_id: str) -> str:
        """
        Returns the path to the aggregated tables JSON file.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            str: The full path to the aggregated/tables.json file.
        """
        return os.path.join(self.get_pipeline_path(pipeline_name, run_id), "aggregated", "tables.json")

    def list_pipelines(self) -> List[str]:
        """
        Lists all available pipeline names.

        Returns:
            List[str]: A list of pipeline names found in the base directory.
        """
        if not os.path.exists(self.base_path):
            return []

        return [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]

    def list_runs(self, pipeline_name: str) -> List[str]:
        """
        Lists all run IDs for a specific pipeline.

        Args:
            pipeline_name (str): The name of the pipeline.

        Returns:
            List[str]: A list of run IDs found for the pipeline.
        """
        pipeline_path = os.path.join(self.base_path, pipeline_name)
        if not os.path.exists(pipeline_path):
            return []

        return [d for d in os.listdir(pipeline_path) if os.path.isdir(os.path.join(pipeline_path, d))]

    def delete_run(self, pipeline_name: str, run_id: str) -> bool:
        """
        Deletes a specific run directory.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.

        Returns:
            bool: True if deleted, False if not found.
        """
        run_path = self.get_pipeline_path(pipeline_name, run_id)
        if os.path.exists(run_path):
            shutil.rmtree(run_path)

            # Clean up pipeline dir if empty
            pipeline_path = os.path.join(self.base_path, pipeline_name)
            try:
                if not os.listdir(pipeline_path):
                    os.rmdir(pipeline_path)
            except OSError:
                pass
            return True
        return False

    def delete_pipeline(self, pipeline_name: str) -> bool:
        """
        Deletes an entire pipeline directory.

        Args:
            pipeline_name (str): The name of the pipeline.

        Returns:
            bool: True if deleted, False if not found.
        """
        pipeline_path = os.path.join(self.base_path, pipeline_name)
        if os.path.exists(pipeline_path):
            shutil.rmtree(pipeline_path)
            return True
        return False

    def clear_all(self):
        """
        Deletes all pipelines and runs.
        """
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)
            os.makedirs(self.base_path)


class Agent0:
    """
    The Orchestrator Agent (Agent 0).

    This agent acts as the main controller for the data extraction pipeline.
    It manages the overall flow, state transitions, and coordination between
    sub-agents (Scanner, Aggregator, Exporter).
    """

    def __init__(self, base_path: str = "pipelines"):
        """
        Initialize the Orchestrator with its sub-agents.

        Args:
            base_path (str): The root directory for storing pipeline data.
        """
        self.fs_manager = FileSystemManager(base_path)

        self.agent1 = Agent1(self.fs_manager)
        self.agent2 = Agent2(self.fs_manager)
        self.agent3 = Agent3(self.fs_manager)

    def create_pipeline(
        self,
        pipeline_name: str,
        input_file_path: str,
        filename: str,
        run_id: str = None,
    ):
        """
        Initialize and setup a new extraction pipeline run.

        This step prepares the filesystem, saves the input file, and sets the
        initial status of the run.

        Args:
            pipeline_name (str): A logical name for the pipeline (e.g., "invoices").
            input_file_path (str): Path to the source file to process.
            filename (str): The name to use for the saved file.
            run_id (str, optional): A unique ID for the run. Auto-generated if None.

        Returns:
            tuple: (run_id, metadata)
        """
        if not run_id:
            run_id = str(uuid.uuid4())

        logger.info(f"Agent 0: Starting pipeline '{pipeline_name}' run '{run_id}'")

        # 1. Setup File System
        self.fs_manager.initialize_pipeline(pipeline_name, run_id)

        # 2. Save Input
        saved_path = self.fs_manager.save_input_file(pipeline_name, run_id, input_file_path, filename)

        # Update metadata
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        metadata["status"] = "READY"
        metadata["input_file"] = saved_path
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        logger.info(f"Agent 0: Pipeline '{pipeline_name}' run '{run_id}' ready. Input saved to {saved_path}")
        return run_id, metadata

    def run_pipeline(
        self, pipeline_name: str, run_id: str, prompt: str = "Extract all tables.", metadata_schema: dict = None
    ):
        """
        Executes the full pipeline lifecycle sequentially.

        1. Scanning & Extraction (Agent 1)
        2. Aggregation (Agent 2)
        3. Export (Agent 3)

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            prompt (str): The extraction instruction prompt for the LLM.
            metadata_schema (dict, optional): The metadata schema to use for extraction.
        """
        logger.info(f"Agent 0: Running pipeline '{pipeline_name}' run '{run_id}'")

        try:
            self.run_scaning_and_extraction(pipeline_name, run_id, prompt, metadata_schema)
            self.run_aggregation(pipeline_name, run_id)
            self.run_export(pipeline_name, run_id)

        except Exception as e:
            logger.error(f"Agent 0: Pipeline failed - {e}")
            metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
            metadata["status"] = "FAILED"
            metadata["error"] = str(e)
            self.fs_manager.save_metadata(pipeline_name, run_id, metadata)
            raise e

    def run_scaning_and_extraction(self, pipeline_name: str, run_id: str, prompt: str, metadata_schema: dict = None):
        """
        Phase 1: Trigger Document Scanning and Extraction.

        Delegates to Agent 1 (Scanner) to process the document page by page.
        """
        logger.info(f"Agent 0: Triggering Scanning & Extraction for '{pipeline_name}' run '{run_id}'")
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        metadata["current_stage"] = "SCANNING"
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        self.agent1.run(pipeline_name, run_id, prompt, metadata_schema)

    def run_aggregation(self, pipeline_name: str, run_id: str):
        """
        Phase 2: Trigger Result Aggregation.

        Delegates to Agent 2 (Aggregator) to combine per-page results.
        """
        logger.info(f"Agent 0: Triggering Aggregation for '{pipeline_name}' run '{run_id}'")
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        metadata["current_stage"] = "AGGREGATING"
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        self.agent2.run(pipeline_name, run_id)

    def run_export(self, pipeline_name: str, run_id: str):
        """
        Phase 3: Trigger Final Export.

        Delegates to Agent 3 (Exporter) to format and save the final output.
        """
        logger.info(f"Agent 0: Triggering Export for '{pipeline_name}' run '{run_id}'")
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        metadata["current_stage"] = "EXPORTING"
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        self.agent3.run(pipeline_name, run_id)
