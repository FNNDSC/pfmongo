from    argparse                    import Namespace
import  asyncio
from    asyncio                     import AbstractEventLoop
from    pfmongo                     import pfmongo
from    pfmongo.models.dataModel    import messageType
from    pfmongo.config              import settings
from    pfmisc                      import Colors as C
from    typing                      import Literal
import  os, sys
from    pathlib                     import Path
import  appdirs
from    pfmongo.models              import dataModel
try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

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

def URI_sanitize(URI:str) -> str:
    return URI.replace(':', '-').replace('/', '')

def stateDir_get() -> Path:
    return Path(appdirs.user_config_dir(appname=__pkg.name))

def session_config(baseDir:Path) -> Path:
    URI:str = URI_sanitize(settings.mongosettings.MD_URI)
    return  baseDir / Path("_MONGO_" + URI)

def sessionUser_notSet() -> int:
    if not settings.mongosettings.MD_sessionUser:
        return complain(f'''
                An 'MD_sessionUser' has not been specified in the environment.
                This variable denotes the "name" of a current user of the service
                and is used to store user specific state data.

                Please set with:

                        export {GR}MD_SESSIONUSER{NC}={CY}yourName{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return 0

def env_statePathSet(options:Namespace) -> bool:
    """
    Check/set a path to contain state/persistent data, typically the
    database name and collection within that database.

    The value is set in the options.statePath, and the return value
    indicates failure/success.

    :param options: the set of options
    :return: 0 -- success, non-zero -- failure
    """
    options.thisSession         = session_config(stateDir_get())
    if sessionUser_notSet():
        return False
    options.sessionUser         = settings.mongosettings.MD_sessionUser
    options.statePath           = options.thisSession   / \
                                  options.sessionUser
    if not options.statePath.exists():
        options.statePath.mkdir(parents = True, exist_ok = True)
    return True

def DB_stateFileResolve(options:Namespace) -> Path:
    return options.statePath / Path(settings.mongosettings.stateDBname)

def collection_stateFileResolve(options:Namespace) -> Path:
    return options.statePath / Path(settings.mongosettings.stateColname)

def DBname_stateFileRead(options:Namespace) -> str:
    contents:str        = ""
    DBstatefile:Path    = DB_stateFileResolve(options)
    if DBstatefile.exists():
        contents        = DBstatefile.read_text()
    return contents

def DBname_stateFileSave(options:Namespace, contents:str) -> str:
    DBstatefile:Path    = DB_stateFileResolve(options)
    DBstatefile.write_text(contents)
    return contents

def DBname_get(options:Namespace) -> str:
    """
    Determine the name of the database within the mongo server to use.

    Order of precedence:
        * if '--DBname' in args, use this as the DBname and set the same
          value in the settings object;
        * if no '--DBname' check for a state file in the options.statePath
          and if this exists, read that file and set the DBname and settings
          object;
        * if neither, then check the settings object and set the DBname to
          that;

    :param options: the set of CLI (and more) options
    :return: a string database name
    """
    if options.DBname:
        settings.mongosettings.MD_DB    = options.DBname
        DBname_stateFileSave(options, options.DBname)
    if not options.DBname:
        DBname:str  = DBname_stateFileRead(options)
        if DBname:
            options.DBname              = DBname
            settings.mongosettings.MD_DB= options.DBname
    if not options.DBname:
        options.DBname                  = settings.mongosettings.MD_DB
    return options.DBname

def env_failCheck(options:Namespace) -> int:
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

    try:
        print(mongodb.responseData.model_dump_json())
    except Exception as e:
        print(mongodb.responseData.model_dump())

    return 0

