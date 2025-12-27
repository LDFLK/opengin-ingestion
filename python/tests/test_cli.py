import os

import pytest
from click.testing import CliRunner

from opengin.tracer.agents.orchestrator import FileSystemManager
from opengin.tracer.cli import cli
import requests


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
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"

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
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"
    
    mock_requests = mocker.patch("opengin.tracer.cli.requests")
    # Fix: Ensure Exception class is catchable
    mock_requests.exceptions.RequestException = requests.exceptions.RequestException

    # Mock response
    mock_response = mocker.Mock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_response.headers = {}
    mock_requests.get.return_value = mock_response

    url = "http://example.com/doc.pdf"

    with runner.isolated_filesystem():
        # verify download happened
        result = runner.invoke(cli, ["run", url])

    assert result.exit_code == 0
    assert f"Downloading PDF from: {url}" in result.output
    assert "Downloaded to temporary file" in result.output

    mock_requests.get.assert_called_once_with(url, stream=True, timeout=60)
    mock_agent_cls.return_value.create_pipeline.assert_called_once()


def test_run_prompt_file(runner, mocker):
    """Test 'run' command reading prompt from a file"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"

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


def test_run_url_failure(runner, mocker):
    """Test 'run' command with a failed URL download"""
    mock_requests = mocker.patch("opengin.tracer.cli.requests")
    mock_requests.exceptions.RequestException = requests.exceptions.RequestException
    
    # Mock raise_for_status to raise an exception
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("404 Not Found")
    mock_requests.get.return_value = mock_response
    
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", "http://example.com/missing.pdf"])
        
    assert result.exit_code != 0
    assert "Error downloading file" in result.output


def test_run_pipeline_failure(runner, mocker):
    """Test 'run' command with a pipeline execution failure"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_fail", {})
    # Simulate a pipeline failure
    mock_agent_instance.run_pipeline.side_effect = Exception("Agent error")
    
    with runner.isolated_filesystem():
        with open("doc.pdf", "wb") as f:
            f.write(b"dummy")
        result = runner.invoke(cli, ["run", "doc.pdf"])
        
    assert result.exit_code != 0
    assert "Pipeline failed: Agent error" in result.output


def test_run_ssrf_protection_private_ip(runner):
    """Test that private IPs are blocked"""
    result = runner.invoke(cli, ["run", "http://192.168.1.1/doc.pdf"])
    assert result.exit_code != 0
    assert "URL resolves to a restricted IP address" in result.output


def test_run_ssrf_protection_loopback(runner):
    """Test that loopback IPs are blocked"""
    result = runner.invoke(cli, ["run", "http://127.0.0.1/doc.pdf"])
    assert result.exit_code != 0
    assert "URL resolves to a restricted IP address" in result.output


def test_run_ssrf_protection_localhost(runner):
    """Test that localhost is blocked"""
    result = runner.invoke(cli, ["run", "http://localhost/doc.pdf"])
    assert result.exit_code != 0
    # The message might be "restricted IP" if it resolves to 127.0.0.1
    # or "Could not resolve" if DNS fails in some envs, but usually it resolves to loopback.
    assert "URL resolves to a restricted IP address" in result.output


def test_run_url_with_query_params(runner, mocker):
    """Test 'run' command with a URL containing query parameters"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"
    
    mock_requests = mocker.patch("opengin.tracer.cli.requests")
    # Fix: Ensure Exception class is catchable
    mock_requests.exceptions.RequestException = requests.exceptions.RequestException

    mocker.patch("opengin.tracer.cli.validate_url", return_value=True)

    mock_response = mocker.Mock()
    mock_response.iter_content.return_value = [b"content"]
    mock_response.headers = {}
    mock_requests.get.return_value = mock_response

    url = "http://example.com/doc.pdf?token=123"

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", url])

    assert result.exit_code == 0
    # Expected behavior: temp file should end with .pdf, not .pdf?token=123
    assert "Downloaded to temporary file" in result.output
    
    args, _ = mock_agent_instance.create_pipeline.call_args
    input_path = args[1] # name, input_path, filename
    assert input_path.endswith(".pdf")
    assert "?" not in input_path


def test_run_url_content_disposition(runner, mocker):
    """Test 'run' command using Content-Disposition filename"""
    mock_agent_cls = mocker.patch("opengin.tracer.cli.Agent0")
    mock_agent_instance = mock_agent_cls.return_value
    mock_agent_instance.create_pipeline.return_value = ("run_123", {})
    mock_agent_instance.fs_manager.get_output_path.return_value = "output_dir"
    
    mock_requests = mocker.patch("opengin.tracer.cli.requests")
    mock_requests.exceptions.RequestException = requests.exceptions.RequestException
    mocker.patch("opengin.tracer.cli.validate_url", return_value=True)

    mock_response = mocker.Mock()
    mock_response.iter_content.return_value = [b"content"]
    # Mock headers with Content-Disposition
    mock_response.headers = {"content-disposition": 'attachment; filename="from_header.pdf"'}
    mock_requests.get.return_value = mock_response

    url = "http://example.com/download"

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", url])

    assert result.exit_code == 0
    assert "Initializing pipeline" in result.output
    
    # Check that create_pipeline was called with the filename from the header
    args, _ = mock_agent_instance.create_pipeline.call_args
    # args: name, input_path, filename
    filename_arg = args[2]
    assert filename_arg == "from_header.pdf"
