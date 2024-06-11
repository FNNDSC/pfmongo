from pfmongo.commands import smash
from pfmongo.models import responseModel
import pfmongo.commands.fop.ls as ls
from argparse import Namespace
import pudb
import ast

from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import ANSI

# from prompt_toolkit.layout import Layout, HSplit, VSplit, FloatContainer, Float
from prompt_toolkit.history import InMemoryHistory
import re

history: InMemoryHistory = InMemoryHistory()


async def fileList_get(options: Namespace) -> list[str]:
    lsFiles: list[str] = []
    lsRet: int = 0
    lsResp: responseModel.mongodbResponse
    lsRet, lsResp = await ls.ls_do(ls.options_add("", "", False, options))

    if lsRet:
        return lsFiles
    try:
        lsFiles = ast.literal_eval(lsResp.message)
    except Exception as e:
        print("error: parsing this 'directory' resulted in a literal_eval exception.")
        print("There might be improperly stored objects.")
    return lsFiles


async def userInput_get(options: Namespace, **kwargs) -> str:
    noninteractive: str = ""
    files: list[str] = []
    # pudb.set_trace()
    for k, v in kwargs.items():
        if k == "noninteractive":
            noninteractive = v
        if k == "files":
            files = ast.literal_eval(v)
    if noninteractive:
        return noninteractive
    userInput: str = ""
    if not len(files):
        files = await fileList_get(options)
    sallcmds: set[str] = set(smash.fscommand)
    snofcmds: set[str] = set(smash.fscommand_noArgs)
    fcmds: list[str] = list(sallcmds.symmetric_difference(snofcmds))
    d_files: dict = {i: None for i in files}
    d_choices: dict = {i: d_files for i in fcmds}
    d_noargs: dict = {i: None for i in snofcmds}
    d_choices = {**d_choices, **d_noargs}
    completer = NestedCompleter.from_nested_dict(d_choices)
    session: PromptSession = PromptSession(history=history)
    smashprompt: str = await smash.prompt_get(options)
    userInput = await session.prompt_async(ANSI(smashprompt), completer=completer)
    return userInput
