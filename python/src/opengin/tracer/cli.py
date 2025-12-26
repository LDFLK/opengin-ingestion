import json
import os

import click
from tabulate import tabulate

from opengin.tracer.agents.orchestrator import FileSystemManager


@click.group()
def cli():
    """
    Pipeline Management CLI.

    Provides commands to inspect, manage, and clean up pipeline runs and their data.
    """


@cli.command()
def list_runs():
    """
    List all pipeline runs.

    Scans the 'pipelines' directory and displays a tabular summary of all recorded runs,
    including their status, page count, and creation timestamp.
    """
    fs_manager = FileSystemManager()
    pipelines = fs_manager.list_pipelines()

    if not pipelines:
        click.echo("No runs found.")
        return

    runs_data = []

    for pipeline_name in pipelines:
        run_ids = fs_manager.list_runs(pipeline_name)
        for run_id in run_ids:
            metadata = fs_manager.load_metadata(pipeline_name, run_id)
            if metadata:
                runs_data.append(
                    [
                        pipeline_name,
                        run_id,
                        metadata.get("status", "UNKNOWN"),
                        metadata.get("page_count", 0),
                        metadata.get("created_at", "N/A"),
                    ]
                )
            else:
                runs_data.append([pipeline_name, run_id, "CORRUPT", 0, "N/A"])

    if runs_data:
        click.echo(
            tabulate(
                runs_data,
                headers=["Pipeline", "Run ID", "Status", "Pages", "Created At"],
                tablefmt="grid",
            )
        )
    else:
        click.echo("No runs found.")


@cli.command()
@click.argument("pipeline_name")
@click.argument("run_id")
def info(pipeline_name, run_id):
    """
    Show details for a specific run.

    Displays the full metadata JSON and lists the generated output files (CSVs)
    for the specified pipeline run.

    Args:
        pipeline_name (str): The name of the pipeline.
        run_id (str): The unique identifier for the run.
    """
    fs_manager = FileSystemManager()
    metadata = fs_manager.load_metadata(pipeline_name, run_id)

    if metadata:
        click.echo(json.dumps(metadata, indent=2))

        # Also list output files
        output_dir = fs_manager.get_output_path(pipeline_name, run_id)
        if os.path.exists(output_dir):
            click.echo("\nOutput Files:")
            for f in os.listdir(output_dir):
                click.echo(f" - {f}")
    else:
        click.echo(f"Run {run_id} not found for pipeline {pipeline_name}.")


@cli.command()
@click.argument("pipeline_name")
@click.argument("run_id")
@click.confirmation_option(prompt="Are you sure you want to delete this run?")
def delete(pipeline_name, run_id):
    """
    Delete a specific run directory.

    Removes all data associated with a single run (metadata, input, intermediate, output).
    If the pipeline directory becomes empty after deletion, it is also removed.

    Args:
        pipeline_name (str): The name of the pipeline.
        run_id (str): The unique identifier for the run.
    """
    fs_manager = FileSystemManager()
    if fs_manager.delete_run(pipeline_name, run_id):
        click.echo(f"Deleted run {run_id} from pipeline {pipeline_name}.")
    else:
        click.echo(f"Run directory not found for pipeline {pipeline_name} run {run_id}")


@cli.command()
@click.argument("pipeline_name")
@click.confirmation_option(prompt="Are you sure you want to delete this ENTIRE pipeline and all its runs?")
def delete_pipeline(pipeline_name):
    """
    Delete an entire pipeline and all its runs.

    Args:
        pipeline_name (str): The name of the pipeline to delete.
    """
    fs_manager = FileSystemManager()
    if fs_manager.delete_pipeline(pipeline_name):
        click.echo(f"Deleted pipeline {pipeline_name} and all its runs.")
    else:
        click.echo(f"Pipeline directory not found: {pipeline_name}")


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to delete ALL pipelines and runs? This cannot be undone.")
def clear_all():
    """
    Delete all pipelines and runs.

    WARNING: This action is irreversible and will wipe the entire 'pipelines' directory.
    """
    fs_manager = FileSystemManager()
    try:
        # Check if there is anything to delete
        if not fs_manager.list_pipelines():
            click.echo("Pipelines directory is already empty.")
            return

        fs_manager.clear_all()
        click.echo("All pipelines and runs have been cleared.")
    except Exception as e:
        click.echo(f"Error clearing all pipelines: {e}")


if __name__ == "__main__":
    cli()
