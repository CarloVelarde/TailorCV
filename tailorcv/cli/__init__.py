"""CLI router for TailorCV commands."""

from __future__ import annotations

import argparse

from tailorcv.cli.generate import main as generate_main
from tailorcv.debug import main as debug_main


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the TailorCV CLI.

    :param argv: Optional argument list for CLI parsing.
    :type argv: list[str] | None
    :return: Exit status (0 for success, 1 for failure).
    :rtype: int
    """
    parser = argparse.ArgumentParser(prog="tailorcv")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "generate",
        help="Generate RenderCV YAML from profile, job, and selection inputs.",
    )
    subparsers.add_parser(
        "debug",
        help="Run the TailorCV smoke test pipeline.",
    )

    parsed, remaining = parser.parse_known_args(argv)

    if parsed.command == "generate":
        return generate_main(remaining)
    if parsed.command == "debug":
        return debug_main(remaining)
    return 1
