import pytest

from opengin.tracer.agents.orchestrator import FileSystemManager


@pytest.fixture
def temp_pipeline_dir(tmp_path):
    """
    Creates a temporary directory for pipelines and initializes FileSystemManager with it.
    """
    pipelines_dir = tmp_path / "pipelines"
    pipelines_dir.mkdir()
    return str(pipelines_dir)


@pytest.fixture
def fs_manager(temp_pipeline_dir):
    return FileSystemManager(base_path=temp_pipeline_dir)


@pytest.fixture
def mock_gemini_response():
    """Returns a mock successful response from Gemini extraction"""
    return {
        "tables": [
            {
                "name": "Invoice Table",
                "columns": ["Item", "Price"],
                "rows": [["Widget A", "10.00"], ["Widget B", "20.00"]],
            }
        ]
    }
