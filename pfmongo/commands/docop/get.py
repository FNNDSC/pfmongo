import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmongo.models import responseModel
from pfmisc import Colors as C
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(id: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "getDocument"
    localoptions.argument = id
    return localoptions


def get_envFailCheck(options: Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    return 0


async def documentGet_asInt(options) -> int:
    fail: int = 0
    if fail := get_envFailCheck(options):
        return fail
    return await driver.run_intReturn(options)


async def documentGet_asModel(options) -> responseModel.mongodbResponse:
    model: responseModel.mongodbResponse = responseModel.mongodbResponse()
    if get_envFailCheck(options):
        model.message = "env failure"
        return model
    return await driver.run_modelReturn(options)


def sync_documentGet_asInt(options: Namespace) -> int:
    return asyncio.run(documentGet_asInt(options))


def sync_documentGet_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(documentGet_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
read and print {PL}document{NC} from a collection

SYNOPSIS
{CY}get {YL}--id <id>{NC}

DESC
This subcommand gets a document with passed 'id' from a collection and
prints it to the console. Use shell redirection to save to disk.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""",
)
@click.option("--id", type=str, help="the document 'id' to get", default="")
@click.pass_context
def get(ctx: click.Context, id: str = "") -> int:
    # pudb.set_trace()
    return sync_documentGet_asInt(options_add(id, ctx.obj["options"]))
