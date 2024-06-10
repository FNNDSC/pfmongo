import click
import click
import pudb
from pfmongo import driver, env
from argparse import Namespace
from pfmongo.models import responseModel
from pfmisc import Colors as C
import copy
from pathlib import Path
from pfmongo.models import fsModel

import pfmongo.commands.smash as smash
import pfmongo.commands.fop.cd as cd
import pfmongo.commands.docop.get as get
from pfmongo.commands.fop.pwd import dir_level
from pfmongo.commands.document import delete as doc
from pfmongo.commands.database import deleteDB as db
from pfmongo.commands.collection import deleteCol as col
import asyncio

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


async def rm_db(options: Namespace) -> responseModel.mongodbResponse:
    resp = await db.DBdel_asModel(
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


async def rm_collection(options: Namespace) -> responseModel.mongodbResponse:
    resp = await col.collectiondel_asModel(
        driver.settmp(
            col.options_add(str(options.file), options),
            [{"beQuiet": True}, {"collectionName": str(options.file)}],
        )
    )
    return resp


async def rm_doc(options: Namespace) -> responseModel.mongodbResponse:
    resp = await doc.deleteDo_asModel(
        driver.settmp(
            doc.options_add(str(options.file.name), options), [{"beQuiet": True}]
        )
    )
    return resp


async def rm_setName(options: Namespace) -> Namespace:
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    cdResp = await cd.toParent(options)
    if cdResp.status:
        options.file = options.file.name
    return options


async def rm_do(options: Namespace) -> responseModel.mongodbResponse:
    cwd: Path = await smash.cwd(options)
    resp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    if not (
        cdResp := await cd.toParent(
            await cd.fullPath_resolve(cd.options_add(options.file, options))
        )
    ).status:
        resp.message = cdResp.message
        return resp
    options.file = Path(options.file.name)
    match dir_level(cdResp):
        case "root":
            resp = await rm_db(options)
        case "database":
            resp = await rm_collection(options)
        case "collection":
            resp = await rm_doc(options)
        case "_":
            resp.message = "invalid directory level"
    print(resp.message)
    await cd.changeDirectory(cd.options_add(str(cwd), options))
    return resp


async def rm_asInt(options: Namespace) -> int:
    resp: responseModel.mongodbResponse = await rm_do(options)
    docDelUsage: responseModel.DocumentDeleteUsage = responseModel.DocumentDeleteUsage()
    docDelUsage.status = resp.status
    return env.response_exitCode(docDelUsage)


async def rm_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return await rm_do(options)


def sync_rm_asInt(options: Namespace) -> int:
    return asyncio.run(rm_asInt(options))


def sync_rm_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(rm_asModel(options))


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
    return sync_rm_asInt(options_add(path, ctx.obj["options"]))
