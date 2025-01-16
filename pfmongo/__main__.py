"""
Program entry point for the pfmongo CLI.

This module initializes the application, processes arguments using
argparse, and invokes the main Click application defined in app_core.py.
"""

import sys
import re
from argparse import ArgumentParser, Namespace
from typing import Sequence, Optional
from pfmongo.pfmongo import (
    options_initialize,
    parser_setup,
    parser_interpret,
)
from pfmongo import env
from pfmongo.app_core import app
from pfmongo.commands import man


# Global options namespace
options: Namespace = Namespace()


def namespace_pubattribs(space: Namespace) -> list[str]:
    """
    Retrieve public attributes from a Namespace object.

    :param space: The Namespace object to analyze.
    :return: A list of public attribute names.
    """
    attributes: list[str] = re.findall(r"\b([A-Za-z][A-Za-z_0-9]*)=", str(space))
    return attributes


def sysargv_revamp(newarg: list[str]) -> list[str]:
    """
    Revamp sys.argv for Click command-line parsing.

    Replaces the current sys.argv with a new set of arguments
    while preserving the executable name.

    :param newarg: A list of new arguments to set.
    :return: The updated sys.argv list.
    """
    executable: str = sys.argv[0]
    sys.argv = [executable] + newarg
    return sys.argv


def cli_entry_point(argv: Optional[list[str]] = None) -> int:
    """
    Core logic for CLI entry, testable separately from Click.

    This function processes core CLI arguments using argparse,
    checks environmental configurations, and prepares for Click dispatch.

    :param argv: A list of CLI arguments (e.g., `["--man"]`).
    :return: 0 on success, or an error code on failure.
    """
    global options
    argv = argv or sys.argv[1:]
    add_help: bool = False

    # Set up and parse arguments using argparse
    parser: ArgumentParser = parser_setup(
        "A client for interacting with MongoDB.", add_help
    )
    options, extra = parser_interpret(parser, argv)

    # Verify environmental state path
    if not env.env_statePathSet(options):
        return 10

    # This is the result of argparse
    if man.coreOptions_show(options):
        return man.man(options)

    # Update sys.argv for Click
    sysargv_revamp(extra)
    return app()


def main(argv: Optional[list[str]] = None) -> int:
    """
    Entry point for the CLI application.

    This wraps the core CLI logic (`cli_entry_point`) to allow system exit handling
    during normal execution.
    """
    try:
        return cli_entry_point(argv)
    except SystemExit as e:
        return e.code


if __name__ == "__main__":
    sys.exit(main())
