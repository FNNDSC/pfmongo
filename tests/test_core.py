import builtins

from _pytest.capture import capsys
from pfmongo import pfmongo
from pfmongo.__main__ import main
import os

os.environ["XDG_CONFIG_HOME"] = "/tmp"
import pytest

from pfmongo.commands.dbop import connect, showAll
from pfmongo.models import responseModel


def CLIcall_parseForStringAndRet(
    capsys, cli: str, contains: str, exitCode: int
) -> None:
    print(f"Testing {cli}")

    ret: int = 0
    try:
        ret = main(cli.split())
    except SystemExit:
        raise
    ret = main(cli.split())
    captured = capsys.readouterr()
    assert ret == exitCode
    assert contains in captured.out


def test_main_manCore(capsys) -> None:
    """core man page"""
    CLIcall_parseForStringAndRet(capsys, "--man", "--useDB <DBname>", 2)


def test_main_version(capsys) -> None:
    """version CLI reporting"""
    CLIcall_parseForStringAndRet(capsys, "--version", "Name", 1)


def test_imp_help(capsys) -> None:
    with pytest.raises(builtins.SystemExit) as exit_info:
        CLIcall_parseForStringAndRet(capsys, "fs imp --help", "imports", 0)

    assert exit_info.value.args == (0,)
