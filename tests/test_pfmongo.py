import builtins
from pathlib            import Path

from _pytest.capture    import capsys
from pfmongo            import pfmongo
from pfmongo.__main__   import main
from pfmongo.pfmongo    import parser_setup, parser_JSONinterpret, parser_interpret
from argparse           import  ArgumentParser, Namespace
import  os
os.environ['XDG_CONFIG_HOME'] = '/tmp'
import              pudb
import              pytest
from                pytest_mock import mocker
from datetime       import datetime
import              time
from typing         import Any
from                unittest.mock   import patch

def CLIcall_parseForStringAndRet(capsys, cli:str, contains:str, exitCode:int) -> None:
    print(f'Testing {cli}')

    ret:int     = main(cli.split())
    captured    = capsys.readouterr()
    assert ret  == exitCode
    assert contains in captured.out

def test_main_manCore(capsys) -> None:
    """
    Test core man page of the app.
    """
    print(f'Testing man page')

    ret:int     = main(['--man'])
    captured    = capsys.readouterr()
    assert ret == 2
    assert '--useDB <DBname>' in captured.out

def test_main_version(capsys) -> None:
    """
    Test version of the app.
    """
    print(f'Testing version page')

    CLIcall_parseForStringAndRet(capsys, "--version", "Name", 1)

    #ret:int     = main(['--version'])
    #captured    = capsys.readouterr()
    #assert ret == 1
    #assert 'Name' in captured.out

def test_imp_help(capsys) -> None:
    with pytest.raises(builtins.SystemExit) as exit_info:
        CLIcall_parseForStringAndRet(capsys, "fs imp --help", "imports", 0)

    assert exit_info.value.args     == (0,)

