import click

from opengin.tracer.cli import cli as tracer_cli


@click.group()
def main():
    """
    OpenGIN CLI - Universal Tool for OpenGIN Ingestion.

    This is the main entry point for the command-line interface.
    It aggregates subcategories of commands, such as 'tracer' for pipeline management.
    """


main.add_command(tracer_cli, name="tracer")

if __name__ == "__main__":
    main()
