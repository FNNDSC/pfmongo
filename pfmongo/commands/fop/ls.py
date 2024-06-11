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
import asyncio
from types import SimpleNamespace
import fontawesome as fa
import shutil

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
    try:
        file: list = ast.literal_eval(resp.message)
        for f in file:
            rstr += objectSymbol_resolve(resp) + f + "  "
    except Exception as e:
        pass
    return rstr


async def ls_db(options: Namespace) -> responseModel.mongodbResponse:
    resp = await db.showAll_asModel(
        driver.settmp(db.options_add(options), [{"beQuiet": True}])
    )
    return resp


async def ls_collection(options: Namespace) -> responseModel.mongodbResponse:
    resp = col.showAll_asModel(
        driver.settmp(col.options_add(options), [{"beQuiet": True}])
    )
    return await resp


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


async def ls_doc(options: Namespace) -> responseModel.mongodbResponse:
    resp = await doc.showAll_asModel(
        driver.settmp(doc.options_add("_id", options), [{"beQuiet": True}])
    )
    if resp.message:
        resp.message = ls_msgParse(resp.message)
    return resp


def ls_msgParse(lstr: str) -> str:
    return re.sub(r"ObjectId\('([\w]+)'\)", r"'\1'", lstr)


async def ls_fargsUpdate(options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    path: Path = await smash.cwd(options)
    cwdSet: set[str] = set(path.parts[-1:])
    argSet: set[str] = set(options.argument.path.parts[-1:])
    try:
        localoptions.argument.path = (argSet - cwdSet).pop()
    except KeyError:
        localoptions.argument.path = Path(".")
    return localoptions


async def ls_do(options: Namespace) -> tuple[int, responseModel.mongodbResponse]:
    cwd: Path = await smash.cwd(options)
    resp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    cdResp: fsModel.cdResponse = fsModel.cdResponse()
    # pudb.set_trace()
    # cd.changeDirectory(cd.options_add(options.argument.path, options))
    if not (
        cdResp := await cd.toDir(
            await cd.fullPath_resolve(cd.options_add(options.argument.path, options))
        )
    ).status:
        resp.message = cdResp.message + " " + cdResp.error
        return 1, resp

    loptions = await ls_fargsUpdate(options)
    match await pwd_level(loptions):
        case "root":
            resp = await ls_db(loptions)
        case "database":
            resp = await ls_collection(loptions)
        case "collection":
            resp = await ls_doc(loptions)
        case "_":
            resp = await ls_db(loptions)
    file_filter(resp, loptions)
    if not options.beQuiet:
        resp_process(resp)
    ret: int = 0
    if not resp.message:
        ret = 1
    await cd.changeDirectory(cd.options_add(str(cwd), options))
    return ret, resp


async def ls_asInt(options: Namespace) -> int:
    ret, resp = await ls_do(options)
    return ret


async def ls_asModel(options: Namespace) -> responseModel.mongodbResponse:
    ret, resp = await ls_do(options)
    return resp


def sync_ls_asInt(options: Namespace) -> int:
    return asyncio.run(ls_asInt(options))


def sync_ls_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(ls_asModel(options))


def terminal_getWidth() -> int:
    return shutil.get_terminal_size().columns


def columns_format(items: list[str], terminal_width: int) -> list[str]:
    """
    Format the given items into columns that fit the terminal width.

    Args:
        items (list[str]): List of strings to format.
        terminal_width (int): Width of the terminal in characters.

    Returns:
        list[str]: List of formatted strings, each representing a row.
    """
    max_item_width: int = max(len(item) for item in items)
    column_width: int = max_item_width + 2  # Add 2 for spacing

    num_columns: int = max(1, terminal_width // column_width)
    num_rows: int = (len(items) + num_columns - 1) // num_columns

    rows: list[str] = []
    for row in range(num_rows):
        row_items: list[str] = items[row::num_rows]
        formatted_row: str = "".join(
            item.ljust(column_width) for item in row_items
        ).rstrip()
        rows.append(formatted_row)

    return rows


def columns_print(items: list[str]) -> None:
    """
    Print the given items in columns that fit the terminal width.

    Args:
        items (list[str]): List of strings to print.
    """
    terminal_width: int = terminal_getWidth()
    formatted_rows: list[str] = columns_format(items, terminal_width)

    for row in formatted_rows:
        print(row)


def filenames_parse(data: str) -> list[str]:
    """
    Parse the data string into a list of filenames.

    Args:
        data (str): The input data string.

    Returns:
        list[str]: List of filenames, each consisting of a type letter, a space, and a string.
    """
    lines: list[str] = data.strip().split("\n")
    filenames: list[str] = [line.strip() for line in lines if line.strip()]
    return filenames


@click.command(
    cls=env.CustomCommand,
    help=f"""
list {YL}path{NC}

SYNOPSIS
{CY}ls {YL}[--attribs {GR}<attriblist>{YL}] [--raw] [--human] [--long] [<path>]{NC}

ARGS
{YL}--long{NC}
This flag triggers a detailed listing, showing analogues to the document
or "file" {CY}owner{NC}, {CY}size{NC}, and creation {CY}date{NC}.

This assumes that the document entry has these fields encoded, which 
is only true for files uploaded using {YL}pfmongo{NC}.

{YL}--raw{NC}
If specified, show the raw response.

{YL}--human{NC}
If specified with {YL}--long{NC} show any sizes in human friendly terms.

{YL}--attribs {GR}<attriblist>{NC}
If specified with {YL}--long{NC} show the passed attributes, specified as 
a comma separated list.

DESCRIPTION
This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.


""",
)
@click.argument("path", required=False)
@click.option(
    "--attribs",
    required=False,
    help="A comma separated list of file attributes to return/print",
)
@click.option(
    "--raw",
    is_flag=True,
    help="print the actual returned response without cleanup",
)
@click.option(
    "--human",
    is_flag=True,
    help="print file sizes in human friendly format",
)
@click.option("--long", is_flag=True, help="If set, use a long listing format")
@click.pass_context
def ls(
    ctx: click.Context, path: str, attribs: str, long: bool, raw: bool, human: bool
) -> int:
    # pudb.set_trace()
    ret, resp = asyncio.run(ls_do(options_add(path, attribs, long, ctx.obj["options"])))
    if raw:
        print(resp.message)
        return ret
    lsd: str = resp_process(resp)
    items: str = "\n".join(lsd.split("  "))
    columns_print(filenames_parse(items))
    return ret
