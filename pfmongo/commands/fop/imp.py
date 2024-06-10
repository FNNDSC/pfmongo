import click
import pudb
from pfmongo import driver, env
import pfmongo.pfmongo
from argparse import Namespace
import json
from pfmisc import Colors as C
from pfmongo.config import settings
from pfmongo.models import responseModel
from typing import Tuple, cast, Callable
from pfmongo.commands.docop import add
from pathlib import Path
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def filename_get(path: str) -> str:
    filename: str = Path(path).name
    return filename


def options_add(file: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(copy.deepcopy(options))
    localoptions.beQuiet = True
    localoptions.do = "import"
    localoptions.argument = {"file": file}
    return localoptions


async def imp_do(options: Namespace) -> responseModel.mongodbResponse:
    imp: responseModel.mongodbResponse = await add.documentAdd_asModel(
        add.options_add(
            options.argument["file"], filename_get(options.argument["file"]), options
        )
    )
    return imp


async def imp_asInt(options: Namespace) -> int:
    imp: responseModel.mongodbResponse = await imp_do(options)
    print(imp.message)
    return 0


def sync_imp_asInt(options: Namespace) -> int:
    return asyncio.run(imp_asInt(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
import a {CY}file{NC} as a {YL}document{NC}

SYNOPSIS
{CY}imp {YL}<file>{NC}

DESC
Import a {YL}file{NC} from the host system into the mongodb as a {YL}document{NC}.

The {YL}file{NC} can have a "path" prefix, denoting a database and collection to
use for the import.

""",
)
@click.argument("file", required=True)
@click.pass_context
def imp(ctx: click.Context, file: str) -> int:
    # pudb.set_trace()
    return sync_imp_asInt(options_add(file, ctx.obj["options"]))
