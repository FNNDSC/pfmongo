import click
import pudb
from pfmongo import driver
from argparse import Namespace
from pfmongo import env
from pfmisc import Colors as C
from pfmongo.config import settings
from pfmongo.commands.clop import connect
from pfmongo.models import responseModel
from typing import cast
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(id: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "deleteDocument"
    localoptions.argument = id
    localoptions.beQuiet = True
    return localoptions


def env_check(options: Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    return 0


def run_check(
    failData: int, message: str = "early failure"
) -> responseModel.mongodbResponse:
    retm: responseModel.mongodbResponse = responseModel.mongodbResponse()
    if failData:
        retm.message = f" {message} (code {failData}) occurred in document delete"
    else:
        retm.status = True
        retm.message = "Initial run_check in document delete ok"
    return retm


async def delete_do(options: Namespace) -> responseModel.mongodbResponse:
    failEnv: int = 0
    if failEnv := env_check(options):
        return run_check(failEnv, "failure in document del setup")
    delResp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    if not (
        delResp := await driver.run_modelReturn(
            await connect.baseCollection_getAndConnect(options)
        )
    ).status:
        pass
        # return delResp
    print(delResp.message)
    if not settings.appsettings.donotFlatten:
        delResp = await driver.run_modelReturn(
            await connect.shadowCollection_getAndConnect(options)
        )
    return delResp


async def deleteDo_asInt(options: Namespace) -> int:
    delResp: responseModel.mongodbResponse = await delete_do(options)
    docDelUse: responseModel.DocumentDeleteUsage = responseModel.DocumentDeleteUsage()
    docDelUse.status = delResp.status
    return env.response_exitCode(docDelUse)


async def deleteDo_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await delete_do(options)


def sync_deleteDo_asInt(options: Namespace) -> int:
    return asyncio.run(deleteDo_asInt(options))


def sync_deleteDo_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(deleteDo_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
remove a {PL}document{NC} from a collection

SYNOPSIS
{CY}delete {GR}--id {YL}<id>{NC}

DESC
This subcommand removes a {PL}document{NC} identified by {YL}<id>{NC} from a collection.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

Use with care. No confirmation is asked!

""",
)
@click.option(
    "--id", type=str, help="Delete the document with the passed 'id'", default=""
)
@click.pass_context
def delete(ctx: click.Context, id: str = "") -> int:
    # pudb.set_trace()
    return sync_deleteDo_asInt(options_add(id, ctx.obj["options"]))
