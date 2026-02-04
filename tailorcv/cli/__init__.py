"""CLI app for TailorCV commands."""

from __future__ import annotations

import typer

from tailorcv.cli.debug import debug
from tailorcv.cli.generate import generate

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="TailorCV CLI for generating RenderCV YAML.",
)

app.command()(generate)
app.command()(debug)
