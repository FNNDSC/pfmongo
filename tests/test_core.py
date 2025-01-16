"""
Test suite for the pfmongo CLI.

This module tests core functionalities of the pfmongo CLI, including
commands like `--man`, `--version`, and specific subcommand help options.
It uses pytest and the `capsys` fixture to capture and validate output.

Helper functions:
- CLIcall_parseForStringAndRet: Simplifies the testing of CLI commands by
  running the command, capturing its output, and verifying expected results.

Tests:
- test_main_manCore: Validates the `--man` option for core manual page output.
- test_main_version: Verifies the `--version` option outputs version info.
- test_imp_help: Ensures the `fs imp --help` command outputs the expected help text.
"""

import builtins
from _pytest.capture import capsys
import pytest
from pfmongo.__main__ import cli_entry_point
import os

# Set the XDG_CONFIG_HOME for temporary testing purposes
os.environ["XDG_CONFIG_HOME"] = "/tmp"


def CLIcall_parseForStringAndRet(
    capsys, cli: str, contains: str, exitCode: int
) -> None:
    """
    Run a CLI command, capture its output, and validate results.

    This helper function invokes the CLI command, checks its exit code, and
    verifies that the output contains the expected substring.

    :param capsys: pytest capture fixture for capturing stdout/stderr.
    :param cli: The CLI command string to test (e.g., "--version").
    :param contains: Substring expected in the captured stdout.
    :param exitCode: Expected exit code of the CLI command.
    :raises AssertionError: If the exit code or output validation fails.
    """
    print(f"Testing {cli}")

    ret: int = 0
    try:
        ret = cli_entry_point(cli.split())
    except SystemExit as e:
        ret = e.code

    captured = capsys.readouterr()
    assert ret == exitCode, f"Expected exit code {exitCode}, got {ret}."
    assert contains in captured.out, f"Expected output to contain: {contains}"


def test_main_manCore(capsys) -> None:
    """
    Test the `--man` option for core manual page output.

    Verifies that running the CLI with `--man` outputs the manual page and
    exits with code 2.
    """
    CLIcall_parseForStringAndRet(capsys, "--man", "python (pf) mongodb client", 2)


def test_main_version(capsys) -> None:
    """
    Test the `--version` option for version information.

    Verifies that running the CLI with `--version` outputs version info and
    exits with code 1.
    """
    CLIcall_parseForStringAndRet(capsys, "--version", "Version:", 1)


def test_imp_help(capsys) -> None:
    """
    Test the help message for the `fs imp` subcommand.

    This test ensures that running `fs imp --help` outputs the expected
    help text for the `imp` subcommand and exits successfully.

    :raises SystemExit: Ensures the subcommand exits with code 0.
    """
    CLIcall_parseForStringAndRet(capsys, "fs imp --help", "import", 0)
