import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmongo.models import responseModel
from pfmisc import Colors as C
import copy

from pfmongo.commands.clop import connect

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(target: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)

    localoptions.do = "searchDocument"
    localoptions.argument = {
        "field": "_id",
        "searchFor": target.split(","),
        "collection": connect.baseCollection_getAndConnect(options).collectionName,
    }
    return localoptions


def sg_asInt(options: Namespace) -> int:
    return driver.run_intReturn(options)


def sg_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)


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
    return sg_asInt(options_add(pattern, ctx.obj["options"]))
