from pfmongo.commands import smash
from pfmongo.models import responseModel
import pfmongo.commands.fop.ls as ls
from argparse import Namespace
import pudb
import ast

from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import ANSI


def fileList_get(options: Namespace) -> list[str]:
    lsFiles: list[str] = []
    lsRet: int = 0
    lsResp: responseModel.mongodbResponse
    lsRet, lsResp = ls.ls_do(ls.options_add("", "", False, options))
    if lsRet:
        return lsFiles
    lsFiles = ast.literal_eval(lsResp.message)
    return lsFiles


def userInput_get(options: Namespace) -> str:
    userInput: str = ""
    files: list[str] = fileList_get(options)
    sallcmds: set[str] = set(smash.fscommand)
    snofcmds: set[str] = set(smash.fscommand_noArgs)
    fcmds: list[str] = list(sallcmds.symmetric_difference(snofcmds))

    d_files: dict = {i: None for i in files}
    d_choices: dict = {i: d_files for i in fcmds}
    d_noargs: dict = {i: None for i in snofcmds}
    d_choices = {**d_choices, **d_noargs}
    completer = NestedCompleter.from_nested_dict(d_choices)
    userInput = prompt(ANSI(smash.prompt_get(options)), completer=completer)
    return userInput
