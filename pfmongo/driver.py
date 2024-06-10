from typing import Callable, Optional, Coroutine
from argparse import Namespace
import asyncio
from asyncio import AbstractEventLoop
import json
import sys
from pfmisc import Colors as C
from pfmongo import pfmongo
from pfmongo.models import responseModel, dataModel
from pfmongo.pfmongo import Pfmongo as MONGO
from pfmongo.config import settings
import copy
import pudb

from typing import Any, Dict, List, Union, cast
from pydantic import BaseModel

try:
    from . import __pkg, __version__
except:
    from pfmongo import __pkg, __version__

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN

# Define a new type that includes all possibilities
NestedDict = Union[str, Dict[str, Any], List[Any]]


class SizeLimitedDict(BaseModel):
    value: NestedDict


def settmp(options: Namespace, newkeyvaluepair: list) -> Namespace:
    """
    set some values (newkeyvaluepair) in a copy of
    <options> and return this copy. Note the original
    <options> is not affected.
    """
    localoptions = copy.deepcopy(options)
    for pair in newkeyvaluepair:
        for k, v in pair.items():
            setattr(localoptions, k, v)
    return localoptions


def get_size(obj: NestedDict) -> int:
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum([get_size(v) for v in obj.values()])
        size += sum([get_size(k) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i) for i in obj])
    return size


def size_limit(obj: Any, limit: int, depth: int) -> NestedDict:
    # if depth == 0 and sys.getsizeof(obj) > limit:
    size: int = get_size(obj)
    if depth == 0 and size > limit:
        # return "size too large"
        return f">>>truncated<<<({str(size)} > {limit})"
    elif isinstance(obj, dict):
        return {k: size_limit(v, limit, depth - 1) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [size_limit(elem, limit, depth - 1) for elem in obj]
    else:
        return obj


def model_pruneForDisplay(model: NestedDict) -> NestedDict:
    if not settings.appsettings.noResponseTruncSize:
        model = size_limit(
            model,
            settings.mongosettings.responseTruncSize,
            settings.mongosettings.responseTruncDepth,
        )
    depthUp: int = 1
    while get_size(model) > settings.mongosettings.responseTruncOver:
        model = size_limit(
            model,
            settings.mongosettings.responseTruncSize,
            settings.mongosettings.responseTruncDepth - depthUp,
        )
        depthUp += 1
    return model


def model_gets(mongodb: MONGO) -> Callable[[bool], str]:
    """return the internal response model as a string"""
    model: NestedDict = {}
    modelForDisplay: NestedDict = {}

    def model_toStr(addModelSizes: bool = False) -> str:
        respstr: str = ""
        if not settings.appsettings.detailedOutput:
            respstr = mongodb.responseData.message
            if settings.appsettings.logging == dataModel.loggingType.NDJSON:
                respstr = f'{{"pfmongo": "{respstr}"}}'
            return respstr
        try:
            respstr = mongodb.responseData.model_dump_json()
        except Exception as e:
            respstr = "%s" % mongodb.responseData.model_dump()
        model = json.loads(respstr)
        modelForDisplay = model_pruneForDisplay(model)
        respstr = json.dumps(modelForDisplay)
        if settings.appsettings.logging == dataModel.loggingType.NDJSON:
            respstr = f'{{"pfmongo": {respstr}}}'
        if addModelSizes:
            respstr += json.dumps(
                {
                    "modelSize": {
                        "orig": get_size(model),
                        "disp": get_size(modelForDisplay),
                    }
                }
            )
        return respstr

    return model_toStr


def responseData_print(mongodb: MONGO) -> None:
    model_asString: Callable[[bool], str] = model_gets(mongodb)
    print(model_asString(settings.appsettings.modelSizesPrint))


def event_setup(
    options: Namespace,
    f_syncCallBack: Optional[Callable[[MONGO], MONGO]] = None,
    # ) -> Callable[..., int | responseModel.mongodbResponse]:
) -> Callable[..., Coroutine[None, None, int | responseModel.mongodbResponse]]:
    # Create the mongodb object...
    mongodb: pfmongo.Pfmongo = pfmongo.Pfmongo(options)

    def payloadAs(returnType: str = "int") -> int | responseModel.mongodbResponse:
        match returnType:
            case "int":
                return mongodb.exitCode
            case "model":
                mongodb.responseData.exitCode = mongodb.exitCode
                return mongodb.responseData
            case _:
                return mongodb.exitCode

    async def run(**kwargs) -> int | responseModel.mongodbResponse:
        nonlocal mongodb
        printResponse: bool = False
        returnType: str = "int"
        for k, v in kwargs.items():
            if k == "printResponse":
                printResponse = v
            if k == "returnType":
                returnType = v

        if not f_syncCallBack:
            # run it asynchronously..!
            loop: AbstractEventLoop

            # If an event loop already exists, use it!
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # Else create a new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            task = loop.create_task(mongodb.service())
            await task
            # try:
            #     loop.run_until_complete(mongodb.service())
            # except Exception as e:
            #     print(f"In event_setup/run: {e}")
        else:
            # else run it with a synchronous callback
            mongodb = f_syncCallBack(mongodb)
        if printResponse and not options.beQuiet:
            responseData_print(mongodb)
        return payloadAs(returnType)

    return run


async def do(
    options: Namespace,
    retType: str,
    f_syncCallBack: Optional[Callable[[MONGO], MONGO]] = None,
) -> int | responseModel.mongodbResponse:
    f = event_setup(options, f_syncCallBack)
    return await f(printResponse=True, returnType=retType)


async def run_intReturn(
    options: Namespace, f_syncCallBack: Optional[Callable[[MONGO], MONGO]] = None
) -> int:
    if not isinstance((result := await do(options, "int", f_syncCallBack)), int):
        raise TypeError("did not receive int as expected")
    return result


async def run_modelReturn(
    options: Namespace, f_syncCallBack: Optional[Callable[[MONGO], MONGO]] = None
) -> responseModel.mongodbResponse:
    if not isinstance(
        (result := await do(options, "model", f_syncCallBack)),
        responseModel.mongodbResponse,
    ):
        raise TypeError("did not receive model as expected")
    return result


def run(
    options: Namespace, f_syncCallBack: Optional[Callable[[MONGO], MONGO]] = None
) -> int:
    # Create the mongodb object...
    mongodb: pfmongo.Pfmongo = pfmongo.Pfmongo(options)

    if not f_syncCallBack:
        # run it asynchronously..!
        loop: AbstractEventLoop = asyncio.get_event_loop()
        loop.run_until_complete(mongodb.service())
    else:
        # else run it with a synchronous callback
        mongodb = f_syncCallBack(mongodb)

    # print responses...
    responseData_print(mongodb)

    # and we're done.
    return mongodb.exitCode
