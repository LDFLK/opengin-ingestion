import json
import os
import tempfile
from datetime import datetime

import click
import requests
from tabulate import tabulate

from opengin.tracer.agents.orchestrator import Agent0, FileSystemManager


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


@cli.command()
@click.argument("input_source")
@click.option("--name", default=None, help="Name of the pipeline run. Defaults to 'run_<timestamp>'.")
@click.option("--prompt", default="Extract all tables.", help="Extraction prompt or path to a text file.")
def run(input_source, name, prompt):
    """
    Run an extraction pipeline.

    INPUT_SOURCE can be a local file path (e.g., ./data/doc.pdf) or a URL (e.g., https://example.com/doc.pdf).

    If INPUT_SOURCE starts with 'http://' or 'https://', it will be downloaded to a temporary location.
    """
    # 1. Handle Prompt Input (String vs File)
    # If the prompt argument is a path to an existing file, read content.
    if os.path.exists(prompt):
        click.echo(f"Loading prompt from file: {prompt}")
        with open(prompt, "r") as f:
            prompt_text = f.read()
    else:
        prompt_text = prompt

    # 2. Handle Input Source (Local vs URL)
    is_url = input_source.startswith("http://") or input_source.startswith("https://")
    input_path = input_source
    temp_file = None

    if is_url:
        click.echo(f"Downloading PDF from: {input_source}")
        try:
            response = requests.get(input_source, stream=True)
            response.raise_for_status()

            # Create temp file
            suffix = os.path.splitext(input_source)[1]
            if not suffix:
                suffix = ".pdf"

            # We create a named temp file but close it so Agent0 can read/copy it safely
            temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
            os.close(temp_fd)

            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            input_path = temp_path
            temp_file = temp_path  # Mark for cleanup
            click.echo(f"Downloaded to temporary file: {input_path}")

        except Exception as e:
            click.echo(f"Error downloading file: {e}", err=True)
            return

    # 3. Setup Pipeline Name
    if not name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"run_{timestamp}"

    # 4. Initialize and Run Agent0
    try:
        agent0 = Agent0()
        filename = os.path.basename(input_source)
        # Sanitise filename for URL
        if is_url:
            # Try to get filename from URL or header, fallback to simple name
            if "?" in filename:
                filename = filename.split("?")[0]
            if not filename:
                filename = "downloaded_doc.pdf"

        click.echo(f"Initializing pipeline '{name}' for file '{filename}'...")
        run_id, metadata = agent0.create_pipeline(name, input_path, filename)

        click.echo(f"Run ID: {run_id}")
        click.echo("Starting extraction...")

        agent0.run_pipeline(name, run_id, prompt_text)

        # 5. Success Output
        click.echo("\nPipeline completed successfully!")

        # Show output files
        fs_manager = agent0.fs_manager
        output_dir = fs_manager.get_output_path(name, run_id)
        if os.path.exists(output_dir):
            click.echo("Output files:")
            for f in os.listdir(output_dir):
                click.echo(f" - {os.path.join(output_dir, f)}")

    except Exception as e:
        click.echo(f"\nPipeline failed: {e}", err=True)

    finally:
        # Cleanup temp file if we downloaded one
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    cli()
