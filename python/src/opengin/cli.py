import click
from opengin.tracer.cli import cli as tracer_cli

@click.group()
def main():
    """OpenGIN CLI - Universal Tool for OpenGIN Ingestion"""
    pass

main.add_command(tracer_cli, name="tracer")

if __name__ == "__main__":
    main()
