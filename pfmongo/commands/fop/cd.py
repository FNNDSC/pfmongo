from argparse import Namespace
import click
from pfmongo import driver, env
from pfmisc import Colors as C
from pfmongo.models import responseModel, fsModel
from pathlib import Path
import pudb

from pfmongo.commands.document import showAll as doc
from pfmongo.commands.state import showAll as state
from pfmongo.commands.database import showAll as mdb
from pfmongo.commands.database import connect as dbconnect
from pfmongo.commands.collection import showAll as col
from pfmongo.commands.collection import connect as colconnect
import pfmongo.commands.smash as smash
import copy
from types import SimpleNamespace
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
YL = C.YELLOW


def options_add(path: str, options: Namespace, create: bool = False) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.beQuiet = True
    localoptions.do = "cd"
    localoptions.cd = SimpleNamespace(**{"path": Path(path), "create": create})
    return localoptions


def path_to_dbCol(options: Namespace) -> tuple:
    path: Path = options.cd.path
    db: str = ""
    collection: str = ""
    match len(path.parts):
        case _ if len(path.parts) == 2:
            (root, db) = path.parts
        case _ if len(path.parts) > 2:
            (root, db, collection) = path.parts[:3]
    return (db, collection)


async def toParent(options: Namespace) -> fsModel.cdResponse:
    return await changeDirectory(options_add(options.cd.path.parent, options))


async def toDir(options: Namespace) -> fsModel.cdResponse:
    (db, collection) = path_to_dbCol(options)
    return await changeDirectory(options_add(f"/{db}/{collection}", options))


async def fullPath_resolve(options: Namespace) -> Namespace:
    async def navigate_cd() -> None:
        ups: str = "../"
        path: Path = await smash.cwd(options)
        cd = str(options.cd.path)
        if cd.startswith(ups):
            if not cd.endswith("/"):
                cd += "/"
            levels_up: int = cd.count(ups)
            try:
                path = path.parents[levels_up - 1] if levels_up > 1 else path.parent
            except Exception:
                path = Path("/")
            cd = cd[len(ups) * levels_up :]
        options.cd.path = path / cd

    def filter_toFirstStarInPath(path: Path) -> Path:
        index = next(
            (i for i, part in enumerate(path.parts) if "*" in part), len(path.parts)
        )
        return Path(*path.parts[:index])

    options.cd.path = filter_toFirstStarInPath(options.cd.path)
    if options.cd.path.is_absolute():
        return options
    if options.cd.path == Path("."):
        options.cd.path = await smash.cwd(options)
    elif options.cd.path == Path(".."):
        path: Path = await smash.cwd(options)
        options.cd.path = path.parent
    elif await smash.cwd(options) == Path("/") and not str(options.cd.path).startswith(
        ".."
    ):
        options.cd.path = Path("/") / options.cd.path
    else:
        await navigate_cd()
    return options


async def db_isListed(db: str, options: Namespace) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    allDB: responseModel.mongodbResponse = await mdb.showAll_asModel(
        driver.settmp(options, [{"do": "showAllDB"}])
    )
    if db not in allDB.message:
        fsPath.error = f"database '{db}' not in mongo"
        fsPath.status = False
        fsPath.code = 2
        fsPath.state["database"] = "void"
    else:
        fsPath.state["database"] = "exists"
    return fsPath


async def db_connect(db: str, options: Namespace) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    fsPath.path = options.cd.path
    if dbConnectFail := await dbconnect.connectTo_asInt(
        dbconnect.options_add(db, options)
    ):
        fsPath.error = f"could not connect to database '{db}'"
        fsPath.status = False
        fsPath.code = 3
        return fsPath
    return fsPath


async def col_isListed(
    db: str, collection: str, options: Namespace
) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    allCollections: responseModel.mongodbResponse = await col.showAll_asModel(
        driver.settmp(options, [{"do": "showAllCollections"}])
    )
    if collection not in allCollections.message:
        fsPath.error = f"collection '{collection}' not in database '{db}'"
        fsPath.status = False
        fsPath.code = 4
        fsPath.state["collection"] = "void"
    else:
        fsPath.state["collection"] = "exists"
    return fsPath


async def col_connect(
    db: str, collection: str, options: Namespace
) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    fsPath.path = options.cd.path
    if colCollectFail := await colconnect.connectTo_asInt(
        colconnect.options_add(collection, options)
    ):
        fsPath.error = (
            f"could not connect to collection '{collection}' in databse '{db}'"
        )
        fsPath.status = False
        fsPath.code = 5
    return fsPath


def is_root(options: Namespace) -> bool:
    b_ret: bool = False
    if not len(options.cd.path.parents):
        env.DBname_stateFileSave(options, "")
        env.collectionName_stateFileSave(options, "")
        b_ret = True
    return b_ret


def is_path_too_long(options) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    if len(options.cd.path.parents) > 2:
        fsPath.error = f"{options.cd.path}: path too long"
        fsPath.status = False
        fsPath.code = 1
    return fsPath


async def path_connect(options: Namespace) -> fsModel.cdResponse:
    fsPath: fsModel.cdResponse = fsModel.cdResponse()
    connect: fsModel.cdResponse = fsModel.cdResponse()
    connect.path = options.cd.path
    if (fsPath := is_path_too_long(options)).code:
        return fsPath
    if is_root(options):
        return connect
    (db, collection) = path_to_dbCol(options)
    if db and not (fsPath := await db_isListed(db, options)).status:
        if not options.cd.create:
            return fsPath
    connect.state["database"] = fsPath.state["database"]
    if db and not (fsPath := await db_connect(db, options)).status:
        return fsPath
    if (
        collection
        and not (fsPath := await col_isListed(db, collection, options)).status
    ):
        if not options.cd.create:
            return fsPath
    connect.state["collection"] = fsPath.state["collection"]
    if collection and not (fsPath := await col_connect(db, collection, options)).status:
        return fsPath
    connect.status = True
    connect.message = f"successfully connected path to {connect.path}"
    connect.code = 0
    env.DBname_stateFileSave(options, db)
    env.collectionName_stateFileSave(options, collection)
    return connect


def path_lengthOK(options: Namespace) -> bool:
    return True if len(options.cd.path.parents.parts == 2) else False


async def changeDirectory(options: Namespace) -> fsModel.cdResponse:
    options = await fullPath_resolve(options)
    cdResponse: fsModel.cdResponse = fsModel.cdResponse()
    if (cdResponse := await path_connect(options)).code:
        print(cdResponse.error)
    return cdResponse


def sync_changeDirectory(options: Namespace) -> fsModel.cdResponse:
    return asyncio.run(changeDirectory(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
change {YL}directory{NC}

SYNOPSIS
{CY}cd {YL}[--create] <path>{NC}

DESC
The {YL}cd{NC} command "changes directory" within a mongodb between a
{CY}<database>{NC} level at the root `/` and a {CY}<collection>{NC} within that
{CY}<database>{NC}. Since there are only ever two "directories" in a
mongodb, trees are not especially nested.

Note that the underlying behaviour is subtly different to a standard
filesystem, and this 'cd' can also "create" a path/directory with if called
with {YL}--create{NC}.

""",
)
@click.argument("path", required=True)
@click.option(
    "--create", is_flag=True, help="If set, also create this path if it does not exist."
)
@click.pass_context
def cd(ctx: click.Context, path: str, create: bool) -> int:
    # pudb.set_trace()
    return sync_changeDirectory(options_add(path, ctx.obj["options"], create)).code
