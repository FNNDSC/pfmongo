from    argparse            import Namespace
import  asyncio
from    asyncio             import AbstractEventLoop
from    pfmongo             import pfmongo
from    pfmongo.models.dataModel import messageType
from    pfmisc              import Colors as C
from    typing              import Literal
import  os, sys
from    pathlib             import Path

NC  = C.NO_COLOUR

def complain(message:str, code:int, level:messageType = messageType.INFO) -> int:
    """
    Generate a "complaint" with a message, code, and info level

    :param message: the message
    :param code: the complaint code
    :param level: the type of complaint
    :return: a complaint code
    """
    match level:
        case messageType.ERROR:
            CL  = C.RED
        case messageType.INFO:
            CL  = C.CYAN
    print(f"\n{CL}{level.name}{NC}")
    if message: print(f"{message}\n")
    return code

def env_failCheck(options:Namespace) -> int:
    if not options.configPath.exists():
        options.configPath.mkdir(parents = True, exist_ok = True)
    if '--help' in sys.argv:
        return 0
    if not options.DBname:
        return complain(f'''
            Unable to determine which database to use.
            A `--useDB` flag with the database name as
            argument must be specified or alternatively
            be set in the environment as MD_DB. ''', 1, messageType.ERROR)
    if not options.collectionName:
        return complain(f'''
            Unable to determine the collection within
            the database {C.YELLOW}{options.DBname}{NC} to use.

            A `--useCollection` flag with the collection
            as argument must be specified. ''', 2,  messageType.ERROR)
    return 0

def run(options:Namespace) -> Literal[1, 0]:

    # Create the mongodb object
    mongodb:pfmongo.Pfmongo     = pfmongo.Pfmongo(options)

    # and run it!
    loop:AbstractEventLoop      = asyncio.get_event_loop()
    loop.run_until_complete(mongodb.service())

    print(mongodb.responseData.model_dump_json())

    return 0

