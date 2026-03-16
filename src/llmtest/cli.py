"""Command-line interface (stub for core architecture)."""

import typer

app = typer.Typer(help="llmtest - pytest for LLM apps")


@app.command()
def run(config: str) -> None:
    """Run tests from a YAML configuration file (not implemented yet)."""
    typer.echo(f"run command called with config: {config}")
    typer.echo("This is a stub - full implementation pending")


@app.command()
def compare(baseline: str, candidate: str) -> None:
    """Compare baseline and candidate configurations (not implemented yet)."""
    typer.echo(f"compare command called with baseline={baseline}, candidate={candidate}")
    typer.echo("This is a stub - full implementation pending")


@app.command()
def init() -> None:
    """Initialize an example project (not implemented yet)."""
    typer.echo("init command called")
    typer.echo("This is a stub - full implementation pending")


if __name__ == "__main__":
    app()
