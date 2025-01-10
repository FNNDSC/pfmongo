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


def options_add(input: str, id: str, options: Namespace) -> Namespace:
    """
    Add options for a document addition operation.

    :param input: Input text (file path or JSON string) to be added.
    :param id: Unique identifier for the document.
    :param options: Namespace object with the current options.
    :return: Updated options Namespace.
    """
    localoptions: Namespace = copy.deepcopy(options)
    localoptions.do = "addDocument"
    localoptions.argument = {"file": input, "id": id}
    return localoptions


def flatten_dict(data: dict, parent_key: str = "", sep: str = "/") -> dict:
    """
    Flatten a nested dictionary into a single level using a separator.

    :param data: Dictionary to flatten.
    :param parent_key: Key of the parent element (used for recursion).
    :param sep: Separator to use for keys in the flattened dictionary.
    :return: Flattened dictionary.
    """
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
    """
    Check the environment and document status.

    :param options: Namespace object with the current options.
    :param d_doc: Document to validate.
    :return: False if the environment or document is invalid, otherwise the document data.
    """
    envFailure: int = env.env_failCheck(options)
    if envFailure:
        return False
    if not d_doc["status"]:
        return not bool(env.complain(d_doc["data"], 1, messageType.ERROR))
    if "data" in d_doc:
        return d_doc["data"]
    else:
        return False


def input_intoDictRead(input: str) -> dict[str, dict | str]:
    """
    Attempt to read input as either a file or a JSON string and parse it into a dictionary.

    :param input: Input text, either a file path or a JSON string.
    :return: A dictionary with the status and parsed data or error details.
    """
    d_json: dict = {"status": False, "input": input, "data": {}}

    # Attempt to open the input as a file
    try:
        with open(input, "r") as f:
            d_json["data"] = json.load(f)
            d_json["status"] = True
            return d_json
    except FileNotFoundError:
        pass  # Input is not a valid file; proceed to JSON parsing
    except Exception as e:
        d_json["data"] = f"File read error: {str(e)}"
        return d_json

    # Attempt to parse the input as a JSON string
    try:
        d_json["data"] = json.loads(input)
        d_json["status"] = True
    except Exception as e:
        d_json["data"] = f"JSON parse error: {str(e)}"

    return d_json


async def prepCollection_forDocument(
    options: Namespace,
    connectCollection: Callable[[Namespace], Awaitable[Namespace]],
    document: dict,
) -> Callable[..., Coroutine[None, None, int | responseModel.mongodbResponse]]:
    """
    Prepare a collection for adding a document.

    :param options: Namespace object with the current options.
    :param connectCollection: Callable to connect to the collection.
    :param document: Document to prepare for insertion.
    :return: Callable for the collection operation.
    """
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
    """
    Add a document to the shadow and primary collections.

    :param document: Document to add.
    :param options: Namespace object with the current options.
    :param modelReturnType: Desired return type ("int" or "model").
    :return: Operation status as an integer or MongoDB response model.
    """
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
                    return int(shadowResp.exitCode)
    if not options.argument["id"] and shadowResp.status:
        document["_id"] = shadowResp.response["connect"].documentName
    run = await prepCollection_forDocument(
        options, connect.baseCollection_getAndConnect, document
    )
    return await run(printResponse=True, returnType=modelReturnType)


def setup(options: Namespace) -> Tuple[int, dict]:
    """
    Set up the environment and validate the input document.

    :param options: Namespace object with the current options.
    :return: Tuple of setup status and document data.
    """
    d_data: dict = {}
    if env.env_failCheck(options):
        return 100, d_data
    d_dataOK: dict | bool = env_OK(
        options, input_intoDictRead(options.argument["file"])
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
    """
    Handle early failures during setup.

    :param failData: Tuple of failure code and data.
    :param returnType: Desired return type ("int" or "model").
    :return: Failure response as an integer or MongoDB response model.
    """
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
    """
    Add a document and return the result in the specified type.

    :param options: Namespace object with the current options.
    :param returnType: Desired return type ("int" or "model").
    :return: Operation status as an integer or MongoDB response model.
    """
    failOrOK: Tuple[int, dict] = (-1, {})
    if (failOrOK := setup(options))[0]:
        return earlyFailure(failOrOK, returnType)
    d_data: dict = failOrOK[1]
    return await add_asType(d_data, options, returnType)


async def documentAdd_asInt(options: Namespace) -> int:
    """
    Add a document and return the result as an integer.

    :param options: Namespace object with the current options.
    :return: Operation status as an integer.
    """
    return cast(int, await documentAdd_asType(options, "int"))


async def documentAdd_asModel(options: Namespace) -> responseModel.mongodbResponse:
    """
    Add a document and return the result as a MongoDB response model.

    :param options: Namespace object with the current options.
    :return: Operation status as a MongoDB response model.
    """
    return cast(
        responseModel.mongodbResponse, await documentAdd_asType(options, "model")
    )


def sync_documentAdd_asInt(options: Namespace) -> int:
    """
    Synchronously add a document and return the result as an integer.

    :param options: Namespace object with the current options.
    :return: Operation status as an integer.
    """
    return asyncio.run(documentAdd_asInt(options))


def sync_documentAdd_asModel(options: Namespace) -> responseModel.mongodbResponse:
    """
    Synchronously add a document and return the result as a MongoDB response model.

    :param options: Namespace object with the current options.
    :return: Operation status as a MongoDB response model.
    """
    return asyncio.run(documentAdd_asModel(options))


@click.command(
    cls=env.CustomCommand,
    help=f"""
add a {PL}document{NC} to a collection

SYNOPSIS
{CY}add {YL}[--input <filename>|<jsonObj>] [--id <value>]{NC}

DESC
This subcommand adds a document to the associated {YL}COLLECTION{NC}.
The document can either be read from a file on the file system or directly
as a JSON serialized string.

A "shadow" document with a flat dataspace is also added to a "shadow"
collection for efficient searching and is kept "in sync" with the original.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.
""",
)
@click.option(
    "--input",
    type=str,
    help="Input as a file path or a JSON serialized string.",
)
@click.option(
    "--id",
    type=str,
    help="If specified, set the 'id' in the mongo collection to the passed string.",
    default="",
)
@click.pass_context
def add(ctx: click.Context, input: str, id: str = "") -> int:
    """
    CLI command to add a document to a MongoDB collection.

    :param ctx: Click context object.
    :param input: Input as a file path or a JSON serialized string.
    :param id: Unique identifier for the document.
    :return: Operation status as an integer.
    """
    return sync_documentAdd_asInt(options_add(input, id, ctx.obj["options"]))
