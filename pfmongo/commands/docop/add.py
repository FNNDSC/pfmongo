import click
import pudb
from pfmongo import driver, env
import pfmongo.pfmongo
from argparse import Namespace
import json
from pfmisc import Colors as C, switch
from pfmongo.config import settings
from pfmongo.models import responseModel
from typing import Tuple, cast, Callable, Coroutine, Awaitable
from pfmongo.commands.clop import connect
from pfmongo.models.dataModel import messageType
import copy
import asyncio

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(file: str, id: str, options: Namespace) -> Namespace:
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "addDocument"
    localoptions.argument = {"file": file, "id": id}
    return localoptions


def flatten_dict(data: dict, parent_key: str = "", sep: str = "/") -> dict:
    flattened: dict = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flattened.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                list_key = f"{new_key}{sep}{i}"
                if isinstance(item, (dict, list)):
                    flattened.update(
                        flatten_dict({str(i): item}, parent_key=list_key, sep=sep)
                    )
                else:
                    flattened[list_key] = item
        else:
            flattened[new_key] = v
    return flattened


def env_OK(options: Namespace, d_doc: dict) -> bool | dict:
    envFailure: int = env.env_failCheck(options)
    if envFailure:
        return False
    if not d_doc["status"]:
        return not bool(env.complain(d_doc["data"], 1, messageType.ERROR))
    if "data" in d_doc:
        return d_doc["data"]
    else:
        return False


def jsonFile_intoDictRead(filename: str) -> dict[bool, dict]:
    d_json: dict = {"status": False, "filename": filename, "data": {}}
    try:
        f = open(filename)
        d_json["data"] = json.load(f)
        d_json["status"] = True
    except Exception as e:
        d_json["data"] = str(e)
    return d_json


async def prepCollection_forDocument(
    options: Namespace,
    connectCollection: Callable[[Namespace], Awaitable[Namespace]],
    document: dict,
    # ) -> Callable[..., int | responseModel.mongodbResponse]:
) -> Callable[..., Coroutine[None, None, int | responseModel.mongodbResponse]]:
    document["_date"] = pfmongo.pfmongo.timenow()
    document["_owner"] = settings.mongosettings.MD_sessionUser
    document["_size"] = driver.get_size(document)
    collection: Namespace = await connectCollection(options)
    return driver.event_setup(
        driver.settmp(
            options,
            [
                {"collectionName": collection.collectionName},
                {"argument": document},
            ],
        )
    )


async def add_asType(
    document: dict, options: Namespace, modelReturnType: str
) -> int | responseModel.mongodbResponse:
    # First save to the shadow collection:
    shadowResp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    if not settings.appsettings.donotFlatten:
        run = await prepCollection_forDocument(
            options, connect.shadowCollection_getAndConnect, flatten_dict(document)
        )
        saveShadowFail: int | responseModel.mongodbResponse = await run(
            printResponse=False, returnType="model"
        )
        shadowResp = cast(responseModel.mongodbResponse, saveShadowFail)
        if not shadowResp.status:
            match modelReturnType:
                case "model":
                    return saveShadowFail
                case "int":
                    return int(not shadowResp.status)
    if not options.argument["id"] and shadowResp.status:
        document["_id"] = shadowResp.response["connect"].documentName
    # Now save to the primary collection
    run = await prepCollection_forDocument(
        options, connect.baseCollection_getAndConnect, document
    )
    return await run(printResponse=True, returnType=modelReturnType)


def setup(options: Namespace) -> Tuple[int, dict]:
    d_data: dict = {}
    if env.env_failCheck(options):
        return 100, d_data
    d_dataOK: dict | bool = env_OK(
        options, jsonFile_intoDictRead(options.argument["file"])
    )
    if not d_dataOK:
        return 100, d_data
    if not isinstance(d_dataOK, dict):
        return 101, d_data
    d_data = d_dataOK
    if len(options.argument["id"]):
        d_data["_id"] = options.argument["id"]
    return 0, d_data


def earlyFailure(
    failData: Tuple[int, dict], returnType: str = "int"
) -> int | responseModel.mongodbResponse:
    reti: int = failData[0]
    retm: responseModel.mongodbResponse = responseModel.mongodbResponse()
    retm.message = f"A setup failure of return {reti} occurred"
    match returnType:
        case "int":
            return reti
        case "model":
            return retm
        case _:
            return reti


async def documentAdd_asType(
    options: Namespace, returnType: str = "int"
) -> int | responseModel.mongodbResponse:
    failOrOK: Tuple[int, dict] = (-1, {})
    if (failOrOK := setup(options))[0]:
        return earlyFailure(failOrOK, returnType)
    d_data: dict = failOrOK[1]
    return await add_asType(d_data, options, returnType)


async def documentAdd_asInt(options: Namespace) -> int:
    return cast(int, await documentAdd_asType(options, "int"))


async def documentAdd_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return cast(
        responseModel.mongodbResponse, await documentAdd_asType(options, "model")
    )


def sync_documentAdd_asInt(options: Namespace) -> int:
    return asyncio.run(documentAdd_asInt(options))


def sync_documentAdd_asModel(options: Namespace) -> responseModel.mongodbResponse:
    return asyncio.run(documentAdd_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
read a {PL}document{NC} from the filesystem and add to a collection

SYNOPSIS
{CY}add {YL}--file <filename> [--id <value>]{NC}

DESC
This subcommand accepts a document {YL}filename{NC} (assumed to contain JSON
formatted contents) and stores the contents in the associated {YL}COLLECTION{NC}.

A "shadow" document with a flat dataspace is also added to a "shadow"
collection. This "shadow" document facilitates searching and is kept
"in sync" with the orginal.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""",
)
@click.option(
    "--file",
    type=str,
    help="The name of a JSON formatted file to save to a COLLECTION in a DATABASE.",
)
@click.option(
    "--id",
    type=str,
    help="If specified, set the 'id' in the mongo collection to the passed string.",
    default="",
)
@click.pass_context
def add(ctx: click.Context, file: str, id: str = "") -> int:
    # pudb.set_trace()
    return sync_documentAdd_asInt(options_add(file, id, ctx.obj["options"]))
