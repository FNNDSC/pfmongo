import click
from argparse import Namespace
from pfmongo import env, driver
from pfmisc import Colors as C

from pfmongo.commands.clop import connect as collection
from pfmongo.models import responseModel
import pudb
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(collection: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "deleteCollection"
    localoptions.argument = collection
    return localoptions


def col_connectToTarget(options: Namespace) -> str:
    currentCol: str = env.collectionName_get(options)
    if currentCol != options.argument:
        options.do = "connectCollection"
        collection.sync_connectTo_asInt(options)
    return options.argument


def collectiondel_setup(options: Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    col_connectToTarget(options)
    options.do = "deleteCollection"
    return 0


async def collectiondel_asInt(options: Namespace) -> int:
    fail: int = 0
    if fail := collectiondel_setup(options):
        return fail
    return await driver.run_intReturn(options)


async def collectiondel_asModel(options: Namespace) -> responseModel.mongodbResponse:
    model: responseModel.mongodbResponse = responseModel.mongodbResponse()
    fail: int = 0
    if fail := collectiondel_setup(options):
        model.message = "env failure"
        return model
    return await driver.run_modelReturn(options)


def sync_collectiondel_asInt(options: Namespace) -> int:
    return asyncio.run(collectiondel_asInt(options))


def sync_collectiondel_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(collectiondel_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
delete an entire {PL}COLLECTION{NC}

SYNOPSIS
{CY}deletecol {YL}<COLLECTION>{NC}

DESC
This subcommand removes an entire {YL}COLLECTION{NC} immediately.
Use with care! The system does not ask for confirmation!
""",
)
@click.argument("collection", required=True)
@click.pass_context
def deleteCol(ctx: click.Context, collection: str) -> int:
    # pudb.set_trace()
    # options:Namespace   = ctx.obj['options']
    return sync_collectiondel_asInt(options_add(collection, ctx.obj["options"]))
