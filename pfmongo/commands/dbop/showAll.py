import asyncio
import click
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo import driver, env
from pfmongo.models import responseModel
import copy
import pudb

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
PL = C.PURPLE


def options_add(options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "showAllDB"
    return localoptions


async def showAll_asInt(options: Namespace) -> int:
    return await driver.run_intReturn(options)


async def showAll_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await driver.run_modelReturn(options)


def sync_showAll_asInt(options: Namespace) -> int:
    return asyncio.run(showAll_asInt(options))


def sync_showAll_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(showAll_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
list {PL}DATABASES{NC} containing data

SYNOPSIS
{CY}showall{NC}

DESC
This command shows all the populated databases available in a given mongodb
server. It accepts no arguments.

""",
)
@click.pass_context
def showAll(ctx: click.Context) -> int:
    return sync_showAll_asInt(options_add(ctx.obj["options"]))
