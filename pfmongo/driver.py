import  pudb
from    typing                      import Callable, Optional
from    pfmongo                     import pfmongo
from    pfmongo.pfmongo             import Pfmongo  as MONGO
from    argparse                    import Namespace
import  asyncio
from    asyncio                     import AbstractEventLoop
from    pfmisc                      import Colors as C
import  sys

try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

def responseData_print(mongodb:MONGO) -> None:
    try:
        print(mongodb.responseData.model_dump_json())
    except Exception as e:
        print(mongodb.responseData.model_dump())

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

