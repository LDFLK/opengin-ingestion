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
    assert not os.path.exists(fs_manager._get_pipeline_path(pipeline_name, run_id))
