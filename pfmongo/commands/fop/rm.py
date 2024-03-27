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
from pfmongo.commands.fop.pwd import dir_level
from pfmongo.commands.document import delete as doc
from pfmongo.commands.database import deleteDB as db
from pfmongo.commands.collection import deleteCol as col

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(file: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "rm"
    localoptions.file = Path(file)
    localoptions.beQuiet = True
    return localoptions


def rm_db(options: Namespace) -> responseModel.mongodbResponse:
    resp = db.DBdel_asModel(
        driver.settmp(
            db.options_add(str(options.file), options),
            [
                {"beQuiet": True},
                {"DBname": str(options.file)},
                {"collectionName": "void"},
            ],
        )
    )
    return resp


def rm_collection(options: Namespace) -> responseModel.mongodbResponse:
    resp = col.collectiondel_asModel(
        driver.settmp(
            col.options_add(str(options.file), options),
            [{"beQuiet": True}, {"collectionName": str(options.file)}],
        )
    )
    return resp


def rm_doc(options: Namespace) -> responseModel.mongodbResponse:
    resp = doc.deleteDo_asModel(
        driver.settmp(
            doc.options_add(str(options.file.name), options), [{"beQuiet": True}]
        )
    )
    return resp


def rm_setName(options: Namespace) -> Namespace:
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    cdResp = cd.toParent(options)
    if cdResp.status:
        options.file = options.file.name
    return options


def rm_do(options: Namespace) -> responseModel.mongodbResponse:
    cwd: Path = smash.cwd(options)
    resp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    if not (
        cdResp := cd.toParent(
            cd.fullPath_resolve(cd.options_add(options.file, options))
        )
    ).status:
        resp.message = cdResp.message
        return resp
    options.file = Path(options.file.name)
    match dir_level(cdResp):
        case "root":
            resp = rm_db(options)
        case "database":
            resp = rm_collection(options)
        case "collection":
            resp = rm_doc(options)
        case "_":
            resp.message = "invalid directory level"
    print(resp.message)
    cd.changeDirectory(cd.options_add(str(cwd), options))
    return resp


def rm_asInt(options: Namespace) -> int:
    resp: responseModel.mongodbResponse = rm_do(options)
    docDelUsage: responseModel.DocumentDeleteUsage = responseModel.DocumentDeleteUsage()
    docDelUsage.status = resp.status
    return env.response_exitCode(docDelUsage)


def rm_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return rm_do(options)


@click.command(
    cls=env.CustomCommand,
    help=f"""
delete {YL}path{NC}

SYNOPSIS
{CY}rm {YL}<path>{NC}

DESC
Delete a {YL}path{NC}. Note that the {YL}<path>{NC} can consist of a
{YL}<path>{NC} prefix specifier denoting the {YL}database{NC} and {YL}collection{NC}
to delete.

""",
)
@click.pass_context
@click.argument("path", required=False)
def rm(ctx: click.Context, path: str) -> int:
    # pudb.set_trace()
    return rm_asInt(options_add(path, ctx.obj["options"]))
