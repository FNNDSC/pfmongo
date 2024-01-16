from    typing                      import Callable, Optional
from    argparse                    import Namespace
import  asyncio
from    asyncio                     import AbstractEventLoop
import  json
import  sys
from    pfmisc                      import Colors as C
from    pfmongo                     import pfmongo
from    pfmongo.models              import responseModel
from    pfmongo.pfmongo             import Pfmongo  as MONGO
from    pfmongo.config              import settings
import  pudb

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

def model_gets(mongodb:MONGO) -> Callable[[bool], str]:
    """ return the internal response model as a string """
    model:NestedDict            = {}
    modelForDisplay:NestedDict  = {}

    def model_toStr(addModelSizes:bool = False) -> str:
        respstr:str             = ""
        if not settings.appsettings.detailedOutput:
            return mongodb.responseData.message
        try:
            respstr = mongodb.responseData.model_dump_json()
        except Exception as e:
            respstr = '%s' % mongodb.responseData.model_dump()
        model           = json.loads(respstr)
        modelForDisplay = model_pruneForDisplay(model)
        respstr         = json.dumps(modelForDisplay)
        if addModelSizes:
            respstr    += json.dumps(
                            {
                                'modelSize': {
                                    'orig' : get_size(model),
                                    'disp' : get_size(modelForDisplay)
                                }
                            }
           )
        return respstr

    return model_toStr

def responseData_print(mongodb:MONGO) -> None:
    model_asString:Callable[[bool], str] = model_gets(mongodb)
    print(model_asString(settings.appsettings.modelSizesPrint))

def event_process(
    options:Namespace,
    f_syncCallBack:Optional[Callable[[MONGO], MONGO]] = None
):
    # Create the mongodb object...
    mongodb:pfmongo.Pfmongo     = pfmongo.Pfmongo(options)

    def payloadAs(returnType:str = 'int') -> int|pfmongo.Pfmongo:
        match returnType:
            case 'int':
                return mongodb.exitCode
            case 'obj':
                return mongodb
            case _ :
                return mongodb.exitCode

    def run(**kwargs) -> int|pfmongo.Pfmongo:
        nonlocal mongodb
        printResponse:bool      = False
        returnType:str          = 'int'
        for k,v in kwargs.items():
            if k == 'printResponse':    printResponse   = v
            if k == 'returnType':       returnType      = v

        if not f_syncCallBack:
            # run it asynchronously..!
            loop:AbstractEventLoop      = asyncio.get_event_loop()
            loop.run_until_complete(mongodb.service())
        else:
            # else run it with a synchronous callback
            mongodb     = f_syncCallBack(mongodb)
        if printResponse:
            responseData_print(mongodb)
        return payloadAs(returnType)

    return run

def do(
    options:Namespace,
    retType:str,
    f_syncCallBack:Optional[Callable[[MONGO], MONGO]] = None
) -> int | pfmongo.Pfmongo:
    f = event_process(options, f_syncCallBack)
    return f(printResponse = True, returnType = retType)

def run_intReturn(
    options:Namespace,
    f_syncCallBack:Optional[Callable[[MONGO], MONGO]] = None
) -> int:
    if not isinstance((result := do(options, 'int', f_syncCallBack)), int):
       raise TypeError("did not receive int as expected")
    return result

def run_modelReturn(
    options:Namespace,
    f_syncCallBack:Optional[Callable[[MONGO], MONGO]] = None
) -> pfmongo.Pfmongo:
    if not isinstance((result := do(options, 'model', f_syncCallBack)), pfmongo.Pfmongo):
       raise TypeError("did not receive model as expected")
    return result

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

