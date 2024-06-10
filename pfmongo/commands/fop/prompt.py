import click
from pfmongo import driver, env
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo.models import responseModel, fsModel
from pathlib import Path
import copy
import ast
import pudb
import asyncio

from pfmongo.commands.document import showAll as doc
from pfmongo.commands.state import showAll as state
import pfmongo.commands.smash as smash
import pfmongo.commands.fop.cd as cd


NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


async def options_add(options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.beQuiet = True
    cwd: responseModel.mongodbResponse = await state.showAll_asModel(localoptions)
    localoptions.cwd = "/" + cwd.message
    return localoptions


def cd_options(options: Namespace) -> Namespace:
    mkdir: bool = True
    return cd.options_add(options.cwd, options, mkdir)


async def prompt_do(options: Namespace) -> fsModel.cdResponse:
    # pudb.set_trace()
    promptResp: fsModel.cdResponse = await cd.changeDirectory(cd_options(options))
    (db, collection) = cd.path_to_dbCol(cd_options(options))
    if db:
        promptResp.message = "/"
        match promptResp.state["database"]:
            case "void":
                promptResp.message += f"{YL}{db}{NC}"
            case "exists":
                promptResp.message += f"{GR}{db}{NC}"
    if collection:
        promptResp.message += "/"
        match promptResp.state["collection"]:
            case "void":
                promptResp.message += f"{YL}{collection}{NC}"
            case "exists":
                promptResp.message += f"{GR}{collection}{NC}"
    return promptResp


async def prompt_asModel(options: Namespace) -> fsModel.cdResponse:
    return await prompt_do(await options_add(options))


async def prompt_asInt(options: Namespace) -> int:
    pathResp: fsModel.cdResponse = await prompt_do(await options_add(options))
    print(pathResp.message)
    return pathResp.code


def sync_prompt_asInt(options: Namespace) -> int:
    return asyncio.run(prompt_asInt(options))


def sync_prompt_asModel(options: Namespace) -> fsModel.cdResponse:
    return asyncio.run(prompt_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
return a {YL}color {CY}aware{NC} prompt

SYNOPSIS
{CY}prompt{NC}

DESC
This command returns a prompt where the color of a directory indicates its
existence in the monogo server: {YL}yellow{NC} indicates the directory is connected,
but empty; {GR}green{NC} indicates connected and has contents.

Only mongodb "directories" that have contents are listable. What this means
in terms of file system analogues is that in a file system a {YL}mkdir{NC}
command actually creates something that at first is empty. In monogo, a
{YL}database{NC} or {YL}collection{NC} is only "really real" once it is not empty.

""",
)
@click.pass_context
def prompt(ctx: click.Context) -> int:
    # pudb.set_trace()
    return sync_prompt_asInt(ctx.obj["options"])
