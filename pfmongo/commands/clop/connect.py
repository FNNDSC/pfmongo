from argparse import Namespace
import click
from pfmisc import Colors as C
from pfmongo import driver, env
from pfmongo.models import responseModel
from pfmongo.config import settings
from typing import Tuple
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(collection: str, options: Namespace) -> Namespace:
    localoptions = copy.deepcopy(options)
    localoptions.do = "connectCollection"
    localoptions.argument = collection
    return localoptions


def is_shadowCollection(collection: str) -> Tuple[str, bool]:
    isShadow: bool = (
        True if collection.endswith(settings.mongosettings.flattenSuffix) else False
    )
    return collection, isShadow


async def baseCollection_getAndConnect(options: Namespace) -> Namespace:
    localoptions = copy.deepcopy(options)
    localoptions.collectionName = env.collectionName_get(localoptions)
    currentCol: str = env.collectionName_get(options)
    if currentCol.endswith(settings.mongosettings.flattenSuffix):
        currentCol = currentCol.rstrip(settings.mongosettings.flattenSuffix)
        localoptions = await collection_connect(currentCol, options)
    return localoptions


async def shadowCollection_getAndConnect(options: Namespace) -> Namespace:
    localoptions = copy.deepcopy(options)
    localoptions.collectionName = env.collectionName_get(localoptions)
    shadowCol: str = ""
    if not (currentCol := is_shadowCollection(env.collectionName_get(options)))[1]:
        shadowSuffix: str = settings.mongosettings.flattenSuffix
        shadowCol = currentCol[0] + shadowSuffix
        localoptions = await collection_connect(shadowCol, options)
    return localoptions


async def collection_connect(collection: str, options: Namespace) -> Namespace:
    """Returns a copy of the options with the following
    state changes:

        1. 'runRet' contains the int result of doing a connection
                    to the <collection>. This run is also performed
                    on its own options copy.
        2. 'collectionName' in the original copy is updated to the
                            <collection>.

    Note the original options passed into this method is *unchanged*!
    """
    return driver.settmp(
        options,
        [
            {
                "runRet": await driver.run_intReturn(
                    driver.settmp(
                        options, [{"do": "connectCollection"}, {"argument": collection}]
                    )
                )
            },
            {"collectionName": collection},
        ],
    )


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
associate context with {PL}COLLECTION{NC}

SYNOPSIS
{CY}connect {YL}<COLLECTION>{NC}

DESC
This command connects to a mongo collection called {YL}COLLECTION{NC}
within a mongo database.

A mongodb "server" can contain several "databases", each of which
contains several "collections".

A {YL}COLLECTION{NC} is the second level of organization in a monogdb.

""",
)
@click.argument("collection", required=True)
@click.pass_context
def connect(ctx: click.Context, collection: str) -> int:
    return sync_connectTo_asInt(options_add(collection, ctx.obj["options"]))
