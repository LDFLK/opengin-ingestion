from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from opengin.tracer.cli import cli
from opengin.tracer.schema import parse_extraction_response
from opengin.tracer.services.gemini import extract_data_with_gemini


@pytest.fixture
def runner():
    return CliRunner()


def test_parse_extraction_response_with_metadata():
    """Test parsing logic when metadata is present in the response"""
    raw_json = """
    {
        "tables": [
            {
                "id": "t1",
                "name": "Table 1",
                "columns": ["Col1", "Col2"],
                "rows": [["Val1", "Val2"]],
                "metadata": {
                    "author": "John Doe",
                    "date": "2023-01-01"
                }
            }
        ]
    }
    """
    result = parse_extraction_response(raw_json)
    assert len(result.tables) == 1
    table = result.tables[0]
    assert table.metadata is not None
    assert table.metadata["author"] == "John Doe"
    assert table.metadata["date"] == "2023-01-01"


def test_extract_data_with_gemini_prompt_construction(mocker):
    """Test that the system prompt includes metadata instructions when schema is provided"""
    # Mock client
    mock_client = mocker.patch("opengin.tracer.services.gemini.client")
    mock_model = MagicMock()
    mock_client.models = mock_model
    mock_client.files.upload.return_value = MagicMock(name="file_name")
    mock_client.files.get.return_value.state = "ACTIVE"

    # Mock genai.Client to ensure 'client' variable in gemini.py is set (if not already by real init)
    # However, gemini.py initializes client at module level. Mocker patch above targets that.

    metadata_schema = {"fields": [{"name": "author", "type": "string"}]}

    extract_data_with_gemini("dummy.pdf", "Extract tables", metadata_schema)

    # Check generate_content call
    mock_client.models.generate_content.assert_called_once()
    args, kwargs = mock_client.models.generate_content.call_args
    # contents arg is passed as keyword or positional? Code uses keyword 'contents'
    contents = kwargs.get("contents")
    assert contents is not None
    assert len(contents) == 2
    system_instruction = contents[1]

    assert "Per Table Metadata Extraction" in system_instruction
    assert "author" in system_instruction


def test_cli_run_with_metadata_schema(runner, mocker):
    """Test CLI run command handles metadata schema argument correctly"""
    # Mock Agent0
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"

    # Create a dummy schema file
    with runner.isolated_filesystem():
        with open("doc.pdf", "wb") as f:
            f.write(b"dummy")

        schema_content = """
        fields:
          - name: author
            type: string
        """
        with open("schema.yaml", "w") as f:
            f.write(schema_content)

        # Mock yaml.safe_load to return the dict
        # We need to mock the import of yaml in cli.py or ensure it succeeds
        # Since imports inside functions are tricky to patch if the module doesn't exist,
        # we can use sys.modules to inject a mock.
        import sys

        mock_yaml = MagicMock()
        mock_yaml.safe_load.return_value = {"fields": [{"name": "author", "type": "string"}]}

        mocker.patch.dict(sys.modules, {"yaml": mock_yaml})
        result = runner.invoke(cli, ["run", "doc.pdf", "--metadata-schema", "schema.yaml"])

    assert result.exit_code == 0

    # Verify Agent0 run_pipeline called with metadata_schema
    mock_agent_instance.run_pipeline.assert_called_once()
    args, kwargs = mock_agent_instance.run_pipeline.call_args
    assert "metadata_schema" in kwargs
    assert kwargs["metadata_schema"]["fields"][0]["name"] == "author"


def test_cli_run_invalid_schema(runner, mocker):
    """Test CLI run command fails with invalid schema"""
    with runner.isolated_filesystem():
        with open("doc.pdf", "wb") as f:
            f.write(b"dummy")

        # Schema missing 'fields'
        with open("invalid_schema.yaml", "w") as f:
            f.write("invalid: yaml")

        import sys

        mock_yaml = MagicMock()
        # Mock what yaml.safe_load returns for invalid input
        mock_yaml.safe_load.return_value = {"invalid": "yaml"}

        mocker.patch.dict(sys.modules, {"yaml": mock_yaml})
        result = runner.invoke(cli, ["run", "doc.pdf", "--metadata-schema", "invalid_schema.yaml"])

    assert result.exit_code != 0
    assert "Invalid schema format" in result.output
