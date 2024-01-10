import  pudb
from    typing                      import Callable, Optional
from    pfmongo                     import pfmongo
from    pfmongo.models              import responseModel
from    pfmongo.pfmongo             import Pfmongo  as MONGO
from    pfmongo.config              import settings
from    argparse                    import Namespace
import  asyncio
from    asyncio                     import AbstractEventLoop
from    pfmisc                      import Colors as C
import  json
import  sys

from typing import Any, Dict, List, Union, cast
from pydantic import BaseModel

try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

# Define a new type that includes all possibilities
NestedDict = Union[str, Dict[str, Any], List[Any]]

class SizeLimitedDict(BaseModel):
    value: NestedDict

def get_size(obj: NestedDict) -> int:
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum([get_size(v) for v in obj.values()])
        size += sum([get_size(k) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i) for i in obj])
    return size

def size_limit(obj: Any, limit: int, depth: int) -> NestedDict:
    # if depth == 0 and sys.getsizeof(obj) > limit:
    size:int    = get_size(obj)
    if depth == 0 and size > limit:
        # return "size too large"
        return f">>>truncated<<<({str(size)} > {limit})"
    elif isinstance(obj, dict):
        return {k: size_limit(v, limit, depth - 1) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [size_limit(elem, limit, depth - 1) for elem in obj]
    else:
        return obj

def model_pruneForDisplay(model:NestedDict) -> NestedDict:
    if not settings.appsettings.noResponseTruncSize:
        model = size_limit(model,
                             settings.mongosettings.responseTruncSize,
                             settings.mongosettings.responseTruncDepth)
    depthUp:int = 1
    while get_size(model) > settings.mongosettings.responseTruncOver:
        model = size_limit(model,
                           settings.mongosettings.responseTruncSize,
                           settings.mongosettings.responseTruncDepth-depthUp)
        depthUp += 1
    return model

def model_gets(mongodb:MONGO) -> tuple[Callable[[], str], NestedDict, NestedDict]:
    """ return the internal response model as a string """
    model:NestedDict            = {}
    modelForDisplay:NestedDict  = {}

    def model_toStr():
        respstr:str             = ""
        if settings.appsettings.conciseOutput:
            return mongodb.responseData.message
        try:
            respstr = mongodb.responseData.model_dump_json()
        except Exception as e:
            respstr = '%s' % mongodb.responseData.model_dump()
        model           = json.loads(respstr)
        modelForDisplay = model_pruneForDisplay(model)
        if settings.appsettings.conciseOutput:
            respstr     = mongodb.responseData.message
        else:
            respstr     = json.dumps(modelForDisplay)
        return respstr

    return model_toStr, model, modelForDisplay

def responseData_print(mongodb:MONGO) -> None:
    model:NestedDict            = {}
    modelForDisplay:NestedDict  = {}
    model_asString, model, modelForDisplay     = model_gets(mongodb)
    print(model_asString())

    if settings.appsettings.modelSizesPrint:
        print(json.dumps(
            {
                'modelSize': {
                    'orig' : get_size(model),
                    'disp' : get_size(modelForDisplay)
                }
            }
        ))

def run(
    options:Namespace,
    f_syncCallBack:Optional[Callable[[MONGO], MONGO]] = None
) -> int:

    # Create the mongodb object...
    mongodb:pfmongo.Pfmongo     = pfmongo.Pfmongo(options)

    if not f_syncCallBack:
        # run it asynchronously..!
        loop:AbstractEventLoop      = asyncio.get_event_loop()
        loop.run_until_complete(mongodb.service())
    else:
        # else run it with a synchronous callback
        mongodb     = f_syncCallBack(mongodb)

    # print responses...
    responseData_print(mongodb)

    # and we're done.
    return mongodb.exitCode

