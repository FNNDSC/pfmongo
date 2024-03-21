import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo.models import responseModel
from typing import Required, cast
import copy
from pfmongo.commands.clop import connect

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
YL = C.YELLOW
PL = C.PURPLE


def options_add(target: str, field: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "searchDocument"
    localoptions.argument = {
        "field": field,
        "searchFor": target.split(","),
        "collection": connect.baseCollection_getAndConnect(options).collectionName,
    }
    return localoptions


def documentSearch_asInt(options: Namespace) -> int:
    return driver.run_intReturn(options)


def documentSearch_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)


@click.command(
    cls=env.CustomCommand,
    help=f"""
find all {PL}documents{NC} containing strings of interest

SYNOPSIS
{CY}search {GR}--target {YL}<stringList>{NC} [{GR}--field {YL}<field>{NC}]

DESC
Search across all documents in a {YL}collection{NC} for any that contain
substrings in the {YL}<stringList>{NC}. This is a comma separated string
of targets to find.

If a {YL}document{NC} contains one (or more) of the {YL}<stringList>{NC} targets
return the value of the {YL}document{NC}'s {YL}<field>{NC}. Typically this is the
document {YL}_id{NC}.

""",
)
@click.option(
    "--target",
    type=str,
    help="A comma separated list. The logical OR of the search is returned",
    default="",
)
@click.option(
    "--field",
    type=str,
    help="List the search hits referenced by this field",
    default="_id",
    required=False,
)
@click.pass_context
def search(ctx: click.Context, target: str, field: str) -> int:
    # pudb.set_trace()
    return documentSearch_asInt(options_add(target, field, ctx.obj["options"]))
