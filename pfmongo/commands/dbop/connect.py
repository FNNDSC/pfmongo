from argparse import Namespace
import click
from pfmisc import Colors as C
from pfmongo import driver, env
from pfmongo.models import responseModel
from copy import deepcopy
import pudb
import asyncio

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
YL = C.YELLOW
PL = C.PURPLE


def options_add(database: str, options: Namespace) -> Namespace:
    localoptions: Namespace = deepcopy(options)
    localoptions.do = "connectDB"
    localoptions.argument = database
    return localoptions


async def connectTo_asInt(options: Namespace) -> int:
    return await driver.run_intReturn(options)


async def connectTo_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await driver.run_modelReturn(options)


def sync_connectTo_asInt(options: Namespace) -> int:
    return asyncio.run(connectTo_asInt(options))


def sync_connectTo_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(connectTo_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
associate a context with {PL}DATABASE{NC}

SYNOPSIS
{CY}connect {YL}<DATABASE>{NC}

DESC
This command connects to a mongo database called {YL}DATABASE{NC}.
A mongodb "server" can contain several "databases". A {YL}DATABASE{NC}
is the lowest (or first) level of organization in monogodb.

In order to do any operations on data, you first MUST connect to
a {PL}DATABASE{NC}.
""",
)
@click.argument("database", required=True)
@click.pass_context
def connect(ctx: click.Context, database: str) -> int:
    return sync_connectTo_asInt(options_add(database, ctx.obj["options"]))
