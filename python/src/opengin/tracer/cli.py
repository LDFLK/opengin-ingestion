import json
import os
import shutil

import click
from tabulate import tabulate

PIPELINES_DIR = "pipelines"


@click.group()
def cli():
    """Pipeline Management CLI"""


def get_run_metadata(pipeline_name, run_id):
    metadata_path = os.path.join(PIPELINES_DIR, pipeline_name, run_id, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return None


@cli.command()
def list_runs():
    """List all pipeline runs."""
    if not os.path.exists(PIPELINES_DIR):
        click.echo("No pipelines directory found.")
        return

    runs_data = []

    for pipeline_name in os.listdir(PIPELINES_DIR):
        pipeline_path = os.path.join(PIPELINES_DIR, pipeline_name)
        if not os.path.isdir(pipeline_path):
            continue

        for run_id in os.listdir(pipeline_path):
            run_path = os.path.join(pipeline_path, run_id)
            if not os.path.isdir(run_path):
                continue

            metadata = get_run_metadata(pipeline_name, run_id)
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
    """Show details for a specific run."""
    metadata = get_run_metadata(pipeline_name, run_id)
    if metadata:
        click.echo(json.dumps(metadata, indent=2))

        # Also list output files
        output_dir = os.path.join(PIPELINES_DIR, pipeline_name, run_id, "output")
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
    """Delete a specific run directory."""
    run_path = os.path.join(PIPELINES_DIR, pipeline_name, run_id)
    if os.path.exists(run_path):
        try:
            shutil.rmtree(run_path)
            click.echo(f"Deleted run {run_id} from pipeline {pipeline_name}.")

            # Use os.rmdir to remove pipeline dir if empty, but suppress error if not empty
            pipeline_path = os.path.join(PIPELINES_DIR, pipeline_name)
            try:
                os.rmdir(pipeline_path)
            except OSError:
                pass

        except Exception as e:
            click.echo(f"Error deleting run: {e}")
    else:
        click.echo(f"Run directory not found: {run_path}")


@cli.command()
@click.argument("pipeline_name")
@click.confirmation_option(prompt="Are you sure you want to delete this ENTIRE pipeline and all its runs?")
def delete_pipeline(pipeline_name):
    """Delete an entire pipeline and all its runs."""
    pipeline_path = os.path.join(PIPELINES_DIR, pipeline_name)
    if os.path.exists(pipeline_path):
        try:
            shutil.rmtree(pipeline_path)
            click.echo(f"Deleted pipeline {pipeline_name} and all its runs.")
        except Exception as e:
            click.echo(f"Error deleting pipeline: {e}")
    else:
        click.echo(f"Pipeline directory not found: {pipeline_name}")


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to delete ALL pipelines and runs? This cannot be undone.")
def clear_all():
    """Delete all pipelines and runs."""
    if os.path.exists(PIPELINES_DIR):
        try:
            # Check if there is anything to delete
            if not os.listdir(PIPELINES_DIR):
                click.echo("Pipelines directory is already empty.")
                return

            # Delete entire pipelines directory content or the directory itself and recreate
            shutil.rmtree(PIPELINES_DIR)
            os.makedirs(PIPELINES_DIR)
            click.echo("All pipelines and runs have been cleared.")
        except Exception as e:
            click.echo(f"Error clearing all pipelines: {e}")
    else:
        click.echo("No pipelines directory found.")


if __name__ == "__main__":
    cli()
