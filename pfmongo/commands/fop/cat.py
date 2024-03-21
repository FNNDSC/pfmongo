import click
import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmongo.models import responseModel
from pfmisc import Colors as C
import copy
from pathlib import Path
from pfmongo.models import fsModel, responseModel

import pfmongo.commands.smash as smash
import pfmongo.commands.fop.cd as cd
import pfmongo.commands.docop.get as get

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(file: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "cat"
    localoptions.file = Path(file)
    localoptions.beQuiet = True
    return localoptions


def path_process(options: Namespace) -> fsModel.cdResponse:
    dir: Path = options.file.parent
    return cd.changeDirectory(cd.options_add(str(dir), options))


def cat_do(options: Namespace) -> int:
    cwd: Path = smash.cwd(options)
    fileDir: fsModel.cdResponse = path_process(options)
    if not fileDir.status:
        print("directory {fileDir.path} does not seem to exist")
    getResponse: responseModel.mongodbResponse = get.documentGet_asModel(
        get.options_add(str(options.file.name), options)
    )
    print(getResponse.message)
    cd.changeDirectory(cd.options_add(str(cwd), options))
    return 0


@click.command(
    cls=env.CustomCommand,
    help=f"""
show {YL}document{NC} contents

SYNOPSIS
{CY}cat {YL}<file>{NC}

DESC
Read a {YL}file{NC} to stdout. Note that the {YL}<file>{NC} can consist of a
{YL}<path>{NC} prefix specifier denoting the {YL}database{NC} and {YL}collection{NC}
to use.

""",
)
@click.pass_context
@click.argument("path", required=False)
def cat(ctx: click.Context, path: str) -> int:
    # pudb.set_trace()
    return cat_do(options_add(path, ctx.obj["options"]))
