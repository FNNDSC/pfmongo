import click
from pfmongo import driver, env
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo.models import fsModel, responseModel
from pathlib import Path
import ast
import pudb
import copy
import re
import fnmatch
import pfmongo.commands.smash as smash
import pfmongo.commands.fop.cd as cd
from pfmongo.commands.document import showAll as doc
from pfmongo.commands.database import showAll as db
from pfmongo.commands.collection import showAll as col
from pfmongo.commands.fop.pwd import pwd_level

from types import SimpleNamespace
import fontawesome as fa

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(path: str, attribs: str, long: bool, options: Namespace) -> Namespace:
    localoptions = copy.deepcopy(options)
    localoptions.do = "ls"
    localoptions.beQuiet = True
    if not path:
        path = "."
    localoptions.argument = SimpleNamespace(
        **{"path": Path(path), "attribs": attribs, "long": long}
    )
    return localoptions


def objectSymbol_resolve(resp: responseModel.mongodbResponse) -> str:
    symbol: str = ""
    match type(resp.response["connect"]):
        case responseModel.showAllDBusage:
            symbol = fa.icons["database"]
        case responseModel.showAllcollectionsUsage:
            symbol = fa.icons["table"]
        case responseModel.DocumentListUsage:
            symbol = fa.icons["file"]
        case _:
            symbol = fa.icons["file"]
    return symbol + " "


def resp_process(resp: responseModel.mongodbResponse) -> str:
    rstr: str = ""
    file: list = ast.literal_eval(resp.message)
    # pudb.set_trace()
    for f in file:
        rstr += objectSymbol_resolve(resp) + f + "  "
    return rstr


def ls_db(options: Namespace) -> responseModel.mongodbResponse:
    resp = db.showAll_asModel(
        driver.settmp(db.options_add(options), [{"beQuiet": True}])
    )
    return resp


def ls_collection(options: Namespace) -> responseModel.mongodbResponse:
    resp = col.showAll_asModel(
        driver.settmp(col.options_add(options), [{"beQuiet": True}])
    )
    return resp


def file_filter(
    resp: responseModel.mongodbResponse, options: Namespace
) -> responseModel.mongodbResponse:
    if options.argument.path != Path("."):
        files: list[str] = eval(resp.message)
        filtered: list[str] = [
            e for e in files if fnmatch.fnmatch(e, options.argument.path)
        ]
        resp.message = "[" + ", ".join([f"'{e}'" for e in filtered]) + "]"
    return resp


def ls_doc(options: Namespace) -> responseModel.mongodbResponse:
    resp = doc.showAll_asModel(
        driver.settmp(doc.options_add("_id", options), [{"beQuiet": True}])
    )
    if resp.message:
        resp.message = ls_msgParse(resp.message)
    return resp


def ls_msgParse(lstr: str) -> str:
    return re.sub(r"ObjectId\('([\w]+)'\)", r"'\1'", lstr)


def ls_fargsUpdate(options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    cwdSet: set[str] = set(smash.cwd(options).parts[-1:])
    argSet: set[str] = set(options.argument.path.parts[-1:])
    try:
        localoptions.argument.path = (argSet - cwdSet).pop()
    except KeyError:
        localoptions.argument.path = Path(".")
    return localoptions


def ls_do(options: Namespace) -> tuple[int, responseModel.mongodbResponse]:
    cwd: Path = smash.cwd(options)
    resp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    # pudb.set_trace()
    # cd.changeDirectory(cd.options_add(options.argument.path, options))
    if not (
        cdResp := cd.toDir(
            cd.fullPath_resolve(cd.options_add(options.argument.path, options))
        )
    ).status:
        resp.message = cdResp.message + " " + cdResp.error
        return 1, resp

    loptions = ls_fargsUpdate(options)
    match pwd_level(loptions):
        case "root":
            resp = ls_db(loptions)
        case "database":
            resp = ls_collection(loptions)
        case "collection":
            resp = ls_doc(loptions)
        case "_":
            resp = ls_db(loptions)
    file_filter(resp, loptions)
    if not options.beQuiet:
        resp_process(resp)
    ret: int = 0
    if not resp.message:
        ret = 1
    cd.changeDirectory(cd.options_add(str(cwd), options))
    return ret, resp


def ls_asInt(options: Namespace) -> int:
    ret, resp = ls_do(options)
    return ret


def ls_asModel(options: Namespace) -> responseModel.mongodbResponse:
    ret, resp = ls_do(options)
    return resp


@click.command(
    cls=env.CustomCommand,
    help=f"""
list {YL}path{NC}

SYNOPSIS
{CY}ls {YL}[--long] [--human] [<path>]{NC}

ARGS
This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.

The {YL}--long{NC} flag triggers a detailed listing, showing analogues to
the document or "file" {CY}owner{NC}, {CY}size{NC}, and creation {CY}date{NC}.
This assumes that the document entry has these fields encoded, which is only
true for files uploaded using {YL}pfmongo{NC}.


""",
)
@click.argument("path", required=False)
@click.option(
    "--attribs",
    required=False,
    help="A comma separated list of file attributes to return/print",
)
@click.option("--long", is_flag=True, help="If set, use a long listing format")
@click.pass_context
def ls(ctx: click.Context, path: str, attribs: str, long: bool) -> int:
    # pudb.set_trace()
    ret, resp = ls_do(options_add(path, attribs, long, ctx.obj["options"]))
    print(resp_process(resp))
    return ret
