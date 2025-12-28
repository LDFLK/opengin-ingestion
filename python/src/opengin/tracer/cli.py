import ipaddress
import json
import os
import re
import socket
import tempfile
from datetime import datetime
from urllib.parse import urlparse

import click
import requests
import yaml
from tabulate import tabulate

from opengin.tracer.agents.orchestrator import Agent0, FileSystemManager


def validate_url(url):
    """
    Validates that the URL does not point to a private, loopback, or reserved IP address.
    Raises click.ClickException if the URL is invalid or unsafe.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise click.ClickException("Invalid URL: No hostname found")

        # Resolve hostname to IP
        try:
            ip_str = socket.gethostbyname(hostname)
        except socket.gaierror:
            raise click.ClickException(f"Could not resolve hostname: {hostname}")

        ip = ipaddress.ip_address(ip_str)

        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast:
            raise click.ClickException(f"URL resolves to a restricted IP address: {ip_str}")

        return True

    except ValueError:
        raise click.ClickException("Invalid URL or IP address format")
    except Exception as e:
        # unexpected error during validation
        raise click.ClickException(f"URL validation failed: {e}")


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
@click.option("--metadata-schema", default=None, help="Path to a YAML file defining the metadata schema.")
def run(input_source, name, prompt, metadata_schema):
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

    # 1.5 Handle Metadata Schema
    schema_content = None
    if metadata_schema:
        if not os.path.exists(metadata_schema):
            raise click.ClickException(f"Metadata schema file not found: {metadata_schema}")

        try:
            with open(metadata_schema, "r") as f:
                schema_content = yaml.safe_load(f)

            # Simple Validation
            if not isinstance(schema_content, dict) or "fields" not in schema_content:
                raise click.ClickException("Invalid schema format. Must typically contain a 'fields' list.")

        except Exception as e:
            raise click.ClickException(f"Error parsing metadata schema: {e}")

    # 2. Handle Input Source (Local vs URL)
    is_url = input_source.startswith("http://") or input_source.startswith("https://")
    input_path = input_source
    # Default filename for local files; overridden for URLs if possible
    filename = os.path.basename(input_source)
    temp_file = None

    if is_url:
        validate_url(input_source)
        click.echo(f"Downloading PDF from: {input_source}")
        try:
            response = requests.get(input_source, stream=True, timeout=60)
            response.raise_for_status()

            # Try to extract filename from Content-Disposition
            content_disposition = response.headers.get("content-disposition")
            if content_disposition:
                # Simple parsing for filename="name"
                fname = re.findall(r'filename="?([^"]+)"?', content_disposition)
                if fname:
                    filename = fname[0]
            else:
                # Fallback to URL path cleaning
                path = urlparse(input_source).path
                filename = os.path.basename(path)

            # Ensure filename isn't empty after fallback
            if not filename or filename == ".":
                filename = "downloaded_doc.pdf"

            # Create temp file
            parsed_url = urlparse(input_source)
            suffix = os.path.splitext(parsed_url.path)[1]
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

        except requests.exceptions.RequestException as e:
            raise click.ClickException(f"Error downloading file: {e}")

    # 3. Setup Pipeline Name
    if not name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"run_{timestamp}"

    # 4. Initialize and Run Agent0
    try:
        agent0 = Agent0()

        click.echo(f"Initializing pipeline '{name}' for file '{filename}'...")
        run_id, metadata = agent0.create_pipeline(name, input_path, filename)

        click.echo(f"Run ID: {run_id}")
        click.echo("Starting extraction...")

        agent0.run_pipeline(name, run_id, prompt_text, metadata_schema=schema_content)

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
        raise click.ClickException(f"Pipeline failed: {e}")

    finally:
        # Cleanup temp file if we downloaded one
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    cli()
