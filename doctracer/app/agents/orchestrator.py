import os
import json
import shutil
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileSystemManager:
    """
    Manages the file system structure for the pipeline.
    
    Structure:
    /pipelines/
      /{pipeline_name}/
        metadata.json
        /input/
        /intermediate/
        /aggregated/
        /output/
    """
    def __init__(self, base_path: str = "pipelines"):
        self.base_path = base_path

    def _get_pipeline_path(self, pipeline_name: str) -> str:
        return os.path.join(self.base_path, pipeline_name)

    def initialize_pipeline(self, pipeline_name: str):
        """Creates the directory structure for a new pipeline run."""
        path = self._get_pipeline_path(pipeline_name)
        
        # Create directories
        os.makedirs(os.path.join(path, "input"), exist_ok=True)
        os.makedirs(os.path.join(path, "intermediate"), exist_ok=True)
        os.makedirs(os.path.join(path, "aggregated"), exist_ok=True)
        os.makedirs(os.path.join(path, "output"), exist_ok=True)
        
        # Initialize metadata
        metadata = {
            "pipeline_name": pipeline_name,
            "created_at": str(datetime.now()),
            "status": "INITIALIZED",
            "page_count": 0,
            "current_stage": "SETUP"
        }
        self.save_metadata(pipeline_name, metadata)
        logger.info(f"Pipeline '{pipeline_name}' initialized at {path}")

    def save_metadata(self, pipeline_name: str, metadata: Dict[str, Any]):
        path = os.path.join(self._get_pipeline_path(pipeline_name), "metadata.json")
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def load_metadata(self, pipeline_name: str) -> Dict[str, Any]:
        path = os.path.join(self._get_pipeline_path(pipeline_name), "metadata.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def save_input_file(self, pipeline_name: str, file_path: str, filename: str) -> str:
        dest_path = os.path.join(self._get_pipeline_path(pipeline_name), "input", filename)
        shutil.copy(file_path, dest_path)
        return dest_path
    
    def save_intermediate_result(self, pipeline_name: str, page_num: int, data: Any):
        path = os.path.join(self._get_pipeline_path(pipeline_name), "intermediate", f"page_{page_num}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load_intermediate_results(self, pipeline_name: str) -> List[Any]:
        intermediate_path = os.path.join(self._get_pipeline_path(pipeline_name), "intermediate")
        results = []
        if not os.path.exists(intermediate_path):
            return results
            
        # Sort by page number to ensure order
        files = sorted(
            [f for f in os.listdir(intermediate_path) if f.startswith("page_") and f.endswith(".json")],
            key=lambda x: int(x.split("_")[1].split(".")[0])
        )
        
        for filename in files:
            with open(os.path.join(intermediate_path, filename), "r") as f:
                results.append(json.load(f))
        return results

    def save_aggregated_result(self, pipeline_name: str, data: Any):
        path = os.path.join(self._get_pipeline_path(pipeline_name), "aggregated", "tables.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_output_path(self, pipeline_name: str) -> str:
        return os.path.join(self._get_pipeline_path(pipeline_name), "output")


class Agent0:
    """
    The Orchestrator Agent.
    Manages the lifecycle of the data extraction pipeline.
    """
    def __init__(self, base_path: str = "pipelines"):
        self.fs_manager = FileSystemManager(base_path)
        from app.agents.scanner import Agent1
        from app.agents.aggregator import Agent2
        from app.agents.exporter import Agent3
        self.agent1 = Agent1(self.fs_manager)
        self.agent2 = Agent2(self.fs_manager)
        self.agent3 = Agent3(self.fs_manager)

    def create_pipeline(self, pipeline_name: str, input_file_path: str, filename: str):
        """Starts a new extraction pipeline."""
        logger.info(f"Agent 0: Starting pipeline '{pipeline_name}'")
        
        # 1. Setup File System
        self.fs_manager.initialize_pipeline(pipeline_name)
        
        # 2. Save Input
        saved_path = self.fs_manager.save_input_file(pipeline_name, input_file_path, filename)
        
        # Update metadata
        metadata = self.fs_manager.load_metadata(pipeline_name)
        metadata["status"] = "READY"
        metadata["input_file"] = saved_path
        self.fs_manager.save_metadata(pipeline_name, metadata)
        
        logger.info(f"Agent 0: Pipeline '{pipeline_name}' ready. Input saved to {saved_path}")
        return metadata

    def run_pipeline(self, pipeline_name: str, prompt: str = "Extract all tables."):
        """Executes the full pipeline flow."""
        logger.info(f"Agent 0: Running pipeline '{pipeline_name}'")
        
        try:
            self.run_scaning_and_extraction(pipeline_name, prompt)
            self.run_aggregation(pipeline_name)
            self.run_export(pipeline_name)
            
            # Temporary success status update
            metadata = self.fs_manager.load_metadata(pipeline_name)
            metadata["status"] = "COMPLETED" # Should be done by last agent
            self.fs_manager.save_metadata(pipeline_name, metadata)
            
        except Exception as e:
            logger.error(f"Agent 0: Pipeline failed - {e}")
            metadata = self.fs_manager.load_metadata(pipeline_name)
            metadata["status"] = "FAILED"
            metadata["error"] = str(e)
            self.fs_manager.save_metadata(pipeline_name, metadata)
            raise e

    def run_scaning_and_extraction(self, pipeline_name: str, prompt: str):
        logger.info(f"Agent 0: Triggering Scanning & Extraction for '{pipeline_name}'")
        metadata = self.fs_manager.load_metadata(pipeline_name)
        metadata["current_stage"] = "SCANNING"
        self.fs_manager.save_metadata(pipeline_name, metadata)
        
        self.agent1.run(pipeline_name, prompt)

    def run_aggregation(self, pipeline_name: str):
        logger.info(f"Agent 0: Triggering Aggregation for '{pipeline_name}'")
        metadata = self.fs_manager.load_metadata(pipeline_name)
        metadata["current_stage"] = "AGGREGATING"
        self.fs_manager.save_metadata(pipeline_name, metadata)
        
        self.agent2.run(pipeline_name)

    def run_export(self, pipeline_name: str):
        logger.info(f"Agent 0: Triggering Export for '{pipeline_name}'")
        metadata = self.fs_manager.load_metadata(pipeline_name)
        metadata["current_stage"] = "EXPORTING"
        self.fs_manager.save_metadata(pipeline_name, metadata)
        
        self.agent3.run(pipeline_name)
