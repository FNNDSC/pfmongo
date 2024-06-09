import click
from argparse import Namespace
import pudb
from typing import Optional, Union, Annotated
from pfmisc import Colors as C
from pfmongo import env, pfmongo, driver
from pfmongo.models import responseModel
import asyncio

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN


def stateResponse_eval(mongodb: pfmongo.Pfmongo) -> pfmongo.Pfmongo:
    mongodb.responseData = mongo_responseEmbed(state_get(mongodb.args))
    mongodb.exitCode = 0
    return mongodb


def state_get(options: Namespace) -> responseModel.stateResponse:
    state: responseModel.stateResponse = responseModel.stateResponse()
    state.database = env.DBname_get(options)
    state.collection = env.collectionName_get(options)
    return state


def mongo_responseEmbed(
    state: responseModel.stateResponse,
) -> responseModel.mongodbResponse:
    return pfmongo.responseData_build(
        {"status": True, "connect": state}, f"{state.database}/{state.collection}"
    )


async def showAll_asInt(options: Namespace) -> int:
    return await driver.run_intReturn(options, stateResponse_eval)


async def showAll_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await driver.run_modelReturn(options, stateResponse_eval)


def sync_showAll_asInt(options: Namespace) -> int:
    return asyncio.run(showAll_asInt(options))


def sync_showAll_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(showAll_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
show internal {GR}state{NC} values

SYNPOSIS
{CY}showall{NC}

DESC
This command shows internal program state. It accepts no arguments.

""",
)
@click.pass_context
def showAll(ctx: click.Context) -> int:
    # pudb.set_trace()
    return sync_showAll_asInt(ctx.obj["options"])
