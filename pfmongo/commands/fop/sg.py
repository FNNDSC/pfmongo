import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmongo.models import responseModel
from pfmisc import Colors as C
import copy
import asyncio
from pfmongo.commands.clop import connect

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


async def options_add(options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)

    localoptions.do = "searchDocument"
    collectionName: Namespace = await connect.baseCollection_getAndConnect(options)
    localoptions.argument = {
        "field": "_id",
        "searchFor": options.pattern.split(","),
        "collection": collectionName.collectionName,
    }
    return localoptions


async def sg_asInt(options: Namespace) -> int:
    return await driver.run_intReturn(await options_add(options))


async def sg_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await driver.run_modelReturn(await options_add(options))


def sync_sg_asInt(options: Namespace) -> int:
    return asyncio.run(sg_asInt(options))


def sync_sg_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(sg_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
sipgrep {YL}pattern{NC}

SYNOPSIS
{CY}sg {YL}<pattern>{NC}

DESC
A pale shadow of "ripgrep", "sipgrep" aims to "sip", or perform an extremely
primitive and simple search across documents, returning the names of documents
(or files) that contain the search pattern.
""",
)
@click.pass_context
@click.argument("pattern", required=True)
def sg(ctx: click.Context, pattern: str) -> int:
    # pudb.set_trace()
    ctx.obj["options"].pattern = pattern
    return sync_sg_asInt(ctx.obj["options"])
