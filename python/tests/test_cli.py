import os

import pytest
from click.testing import CliRunner

from opengin.tracer.agents.orchestrator import FileSystemManager
from opengin.tracer.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_pipeline_data(temp_pipeline_dir):
    """Creates some dummy pipeline data for CLI tests"""
    fs_manager = FileSystemManager(base_path=str(temp_pipeline_dir))
    pipeline_name = "cli_test_pipeline"
    run_id = "cli_run_1"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Save dummy output
    output_dir = fs_manager.get_output_path(pipeline_name, run_id)
    with open(os.path.join(output_dir, "test.csv"), "w") as f:
        f.write("col1,col2\nval1,val2")

    return pipeline_name, run_id


def test_list_runs(runner, test_pipeline_data, temp_pipeline_dir):
    # We need to monkeypatch PIPELINES_DIR logic in cli.py implicitly?
    # No, cli.py now uses FileSystemManager() which defaults to "pipelines" in CWD.
    # We need to mock FileSystemManager in cli.py to use our temp dir.
    # OR, we change CWD to tmp_path.

    pipeline_name, run_id = test_pipeline_data

    with runner.isolated_filesystem(temp_dir=temp_pipeline_dir) as _:
        # The temp_pipeline_dir fixture already created "pipelines" inside tmp_path.
        # But isolated_filesystem creates a NEW empty temp dir and cd's into it.
        # We want to use the directory structure prepared by `test_pipeline_data`.
        pass

    # Better approach: Patch FileSystemManager in cli.py to return our instance
    # or patch the base path DEFAULT.
    # Actually, orchestrator.py FileSystemManager init defaults to "pipelines".
    # If we run the CLI from a directory containing "pipelines", it works.

    # Let's change CWD to the temp_pipeline_dir PARENT.
    # temp_pipeline_dir is path/to/tmp/pipelines.
    # parent is path/to/tmp.

    (
        os.path.dirname(os.path.dirname(test_pipeline_data[0]))
        if isinstance(test_pipeline_data, tuple)
        else os.path.dirname(temp_pipeline_dir)
    )
    # The fixture returns paths but temp_pipeline_dir is actually a path string from conftest.

    # conftest: pipelines_dir = tmp_path / "pipelines"; return str(pipelines_dir)
    parent_dir = os.path.dirname(temp_pipeline_dir)

    # We change directory to parent_dir where "pipelines" exists.
    os.chdir(parent_dir)

    result = runner.invoke(cli, ["list-runs"])
    assert result.exit_code == 0
    assert pipeline_name in result.output
    assert run_id in result.output


def test_info_command(runner, test_pipeline_data, temp_pipeline_dir):
    pipeline_name, run_id = test_pipeline_data
    parent_dir = os.path.dirname(temp_pipeline_dir)
    os.chdir(parent_dir)

    result = runner.invoke(cli, ["info", pipeline_name, run_id])
    assert result.exit_code == 0
    assert "test.csv" in result.output
    assert '"status": "INITIALIZED"' in result.output


def test_delete_run(runner, test_pipeline_data, temp_pipeline_dir):
    pipeline_name, run_id = test_pipeline_data
    parent_dir = os.path.dirname(temp_pipeline_dir)
    os.chdir(parent_dir)

    result = runner.invoke(cli, ["delete", pipeline_name, run_id], input="y\n")
    assert result.exit_code == 0
    assert f"Deleted run {run_id}" in result.output

    fs_manager = FileSystemManager(base_path=temp_pipeline_dir)
    assert not os.path.exists(fs_manager.get_pipeline_path(pipeline_name, run_id))


def test_run_local_file(runner, mocker, temp_pipeline_dir):
    """Test 'run' command with a local file"""
    # Mock Agent0
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.run_pipeline.return_value = None

    # Mock output path existence check to avoid "Output files:"
    # section erroring or verify it prints nothing if not exists
    # We can just let it run.

    with runner.isolated_filesystem():
        with open("doc.pdf", "wb") as f:
            f.write(b"dummy content")

        result = runner.invoke(cli, ["run", "doc.pdf", "--name", "test_run", "--prompt", "test prompt"])

    assert result.exit_code == 0
    assert "Initializing pipeline 'test_run'" in result.output
    assert "Pipeline completed successfully!" in result.output

    mock_agent_instance.create_pipeline.assert_called_once()
    mock_agent_instance.run_pipeline.assert_called_once()
    args, _ = mock_agent_instance.run_pipeline.call_args
    assert args[2] == "test prompt"


def test_run_url(runner, mocker):
    """Test 'run' command with a URL"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_requests = mocker.patch("opengin.tracer.cli.requests")

    # Mock response
    mock_response = mocker.Mock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_requests.get.return_value = mock_response

    url = "http://example.com/doc.pdf"

    with runner.isolated_filesystem():
        # verify download happened
        result = runner.invoke(cli, ["run", url])

    assert result.exit_code == 0
    assert f"Downloading PDF from: {url}" in result.output
    assert "Downloaded to temporary file" in result.output

    mock_requests.get.assert_called_once_with(url, stream=True)
    mock_agent_cls.return_value.create_pipeline.assert_called_once()


def test_run_prompt_file(runner, mocker):
    """Test 'run' command reading prompt from a file"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})

    prompt_content = "This is a complex prompt from file."

    with runner.isolated_filesystem():
        with open("doc.pdf", "wb") as f:
            f.write(b"dummy")
        with open("prompt.txt", "w") as f:
            f.write(prompt_content)

        result = runner.invoke(cli, ["run", "doc.pdf", "--prompt", "prompt.txt"])

    assert result.exit_code == 0
    assert "Loading prompt from file: prompt.txt" in result.output

    # Verify the content was passed, not the filename
    mock_agent_instance.run_pipeline.assert_called_once()
    args, _ = mock_agent_instance.run_pipeline.call_args
    assert args[2] == prompt_content
