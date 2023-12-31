import  sys
import  pudb
from    typing                      import Callable, Optional
from    argparse                    import Namespace
import  asyncio
from    asyncio                     import AbstractEventLoop
from    pfmongo.models.dataModel    import messageType
from    pfmongo.config              import settings
from    pfmisc                      import Colors as C
from    typing                      import Literal
import  os, sys
from    pathlib                     import Path
import  appdirs
from    pfmongo.models              import dataModel, responseModel
from    typing                      import Callable, Optional, Any
try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
LR  = C.LIGHT_RED

def complain(
        message:str,
        code:int,
        level:messageType = messageType.INFO
) -> int:
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
    if settings.appsettings.logging == dataModel.loggingType.CONSOLE:
        print(f"\n{CL}{level.name}{NC}")
        if message:
            print(f"{message}")
    else:
        print(f'{{"level": "{level.name}"}}')
        pudb.set_trace()
        if message: print(f'{{"message": "{to_singleLine(message)}"}}')
    return code

def to_singleLine(message:str) -> str:
    return message.replace('\n', ' ')

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

def response_exitCode(var:      responseModel.databaseDesc  |\
                                responseModel.collectionDesc
) -> int:
    exitCode:int    = 0
    match var:
        case responseModel.databaseDesc() | responseModel.collectionDesc():
            exitCode    = 0 if var.info.connected else 100
        case responseModel.DocumentAddUsage():
            exitCode    = 0 if var.status else 101
    return exitCode

def databaseOrCollectionDesc_message(var:responseModel.databaseDesc|\
                                         responseModel.collectionDesc) -> str:
    messge:str  = ""
    message     = f'Success while connecting {var.otype}: "{var.name}"'\
                    if var.info.connected else \
                  f'Could not connect to mongo {var.otype}: "{var.name}"'
    return message

def documentAddUsage_message(var:responseModel.DocumentAddUsage) -> str:
    message:str = ""
    name:str    = var.document['_id']
    db:str      = var.collection.databaseName
    col:str     = var.collection.name
    size:int    = 0
    if '_size' in var.document:
        size    = var.document['_size']
    message     = f'Successfully added "{name} (size {size}) to {db}/{col}' \
                    if var.status else \
                  f'Could not add "{name}" (size {size}) to {db}/{col}'
    return message

def response_messageDesc(var:   responseModel.databaseDesc      |\
                                responseModel.collectionDesc
) -> str:
    message:str     = ""
    match var:
        case responseModel.databaseDesc() | responseModel.collectionDesc():
            message = databaseOrCollectionDesc_message(var)
        case responseModel.DocumentAddUsage():
            message = documentAddUsage_message(var)
    return message

def connectDB_failureCheck(
        connection:responseModel.databaseDesc
) -> responseModel.databaseDesc:
    if not connection.info.connected:
        complain(f'''
                A database connection error has occured. This typically means
                that the mongo DB service has either not been started or has
                not been specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}

                Alternatively, check the mongo service credentials:

                        {GR}export {CY}MD_USERNAME=<user>{NC} && \\
                        {GR}export {CY}MD_PASSWORD=<password>{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return connection

def connectCollection_failureCheck(
        connection:responseModel.collectionDesc
) -> responseModel.collectionDesc:
    if not connection.info.connected:
        complain(f'''
                A collection connection error has occured. This typically means
                that an connection error was triggered in the housing database.
                Usually this means that the mongo DB service itself has either
                not been started or has not been specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}

                Alternatively, check the mongo service credentials:

                        {GR}export {CY}MD_USERNAME=<user>{NC} && \\
                        {GR}export {CY}MD_PASSWORD=<password>{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return connection


def showAllcollections_failureCheck(
        usage:responseModel.showAllcollectionsUsage
) -> responseModel.showAllcollectionsUsage:
    if not usage.info.connected:
        complain(f'''
                Unable to show all the collections in the database. This typically means
                that the mongo DB service has either not been started or has not been
                specified correctly, or has incorrect credentialling, or other issues.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return usage

def showAllDBUsage_failureCheck(
        usage:responseModel.showAllDBusage
) -> responseModel.showAllDBusage:
    if not usage.info.connected:
        complain(f'''
                Unable to show all databases in the server. This typically means
                that the mongo DB service has either not been started or has not been
                specified correctly, or has incorrect credentialling, or other issues.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return usage

def usage_failureCheck(
        usage:responseModel.databaseNamesUsage|responseModel.collectionNamesUsage
) -> responseModel.databaseNamesUsage|responseModel.collectionNamesUsage:
    if not usage.info.connected:
        complain(f'''
                A usage error has occured. This typically means that the
                mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    return usage

def addDocument_failureCheck(
        usage:responseModel.DocumentAddUsage
) -> responseModel.DocumentAddUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(f'''
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    if not usage.status:
        complain(f'''
                A document add usage error has occured, reported as:

                {LR}{usage.resp['error']}{NC}

                This typically means that a duplicate 'id' has been specified.
                Please check the value of any

                    {CY}--id {GR}<value>{NC}

                 in the {GR}add{NC} subcommand.
                ''',
                6,
                dataModel.messageType.ERROR)

    return usage

def deleteDocument_failureCheck(
        usage:responseModel.DocumentDeleteUsage
) -> responseModel.DocumentDeleteUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(f'''
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    if not usage.status:
        complain(f'''
                A document delete usage error has occured. This typically means that
                a duplicate 'id' has been specified. Please check the value of any

                    {CY}--id {GR}<value>{NC}

                 in the {GR}delete{NC} subcommand.
                ''',
                6,
                dataModel.messageType.ERROR)

    return usage

def listDocument_failureCheck(
        usage:responseModel.DocumentListUsage
) -> responseModel.DocumentListUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(f'''
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                7,
                dataModel.messageType.ERROR)
    if not usage.status:
        complain(f'''
                A document list usage error has occured. This typically means that
                a non existant search query field has been specified. Please check
                the value of any

                    {CY}--field {GR}<value>{NC}

                 in the {GR}list{NC} subcommand.
                ''',
                8,
                dataModel.messageType.ERROR)

    return usage

def getDocument_failureCheck(
        usage:responseModel.DocumentGetUsage
) -> responseModel.DocumentGetUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(f'''
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                7,
                dataModel.messageType.ERROR)
    if not usage.status:
        complain(f'''
                A document list get error has occured. This typically means that
                no document in the collection had a matching id term. Please check
                the value of any

                    {CY}--id {GR}<value>{NC}

                 in the {GR}get{NC} subcommand.
                ''',
                8,
                dataModel.messageType.ERROR)

    return usage

def searchDocument_failureCheck(
        usage:responseModel.DocumentSearchUsage
) -> responseModel.DocumentSearchUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(f'''
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                ''',
                7,
                dataModel.messageType.ERROR)
    if not usage.status:
        complain(f'''
                A document search usage error has occured. This typically means that
                a non existant search query field has been specified. Please check
                the value of any

                    {CY}--field {GR}<value>{NC}

                 in the {GR}search{NC} subcommand.
                ''',
                8,
                dataModel.messageType.ERROR)

    return usage

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
    statefile:Path      = DB_stateFileResolve(options)
    if statefile.exists():
        contents        = statefile.read_text()
    return contents

def DBname_stateFileSave(options:Namespace, contents:str) -> str:
    statefile:Path      = DB_stateFileResolve(options)
    statefile.write_text(contents)
    return contents

def collectionName_stateFileRead(options:Namespace) -> str:
    contents:str        = ""
    statefile:Path      = collection_stateFileResolve(options)
    if statefile.exists():
        contents        = statefile.read_text()
    return contents

def collectionName_stateFileSave(options:Namespace, contents:str) -> str:
    statefile:Path      = collection_stateFileResolve(options)
    statefile.write_text(contents)
    return contents

def stateFileSave(
        options:Namespace,
        contents:str,
        f_stateFileResolve: Callable[[Namespace], Path]
) -> str:
    statefile:Path      = f_stateFileResolve(options)
    statefile.write_text(contents)
    return contents

def stateFileRead(
        options:Namespace,
        f_stateFileResolve:Callable[[Namespace], Path]
    ) -> str:
    contents:str        = ""
    statefile:Path      = f_stateFileResolve(options)
    if statefile.exists():
        contents        = statefile.read_text()
    return contents

def collectionName_get(options:Namespace) -> str:
    """
    Determine the name of the collection within the mongo server to use.

    Order of precedence:
        * if '--useCollection' (collectionName) in args, use this as
          the collection and set the same value in the settings object;
        * if no '--useCollection', check for a state file in the options.statePath
          and if this exists, read that file and set the collectionName and
          settings object;
        * if neither, then check the settings object and set the collectionName
          to that;
        * otherwise, failing everything, return an empty string.

    :param options: the set of CLI (and more) options
    :return: a string database name
    """
    if options.collectionName:
        settings.mongosettings.MD_COLLECTION = options.collectionName
        collectionName_stateFileSave(options, options.collectionName)
    if not options.collectionName:
        collectionName:str      = collectionName_stateFileRead(options)
        if collectionName:
            options.collectionName                  = collectionName
            settings.mongosettings.MD_COLLECTION    = options.DBname
    if not options.collectionName:
        options.collectionName  = settings.mongosettings.MD_COLLECTION
    return options.collectionName

def DBname_get(options:Namespace) -> str:
    """
    Determine the name of the database within the mongo server to use.

    Order of precedence:
        * if '--useDB' (i.e. DBname) in args, use this as the DBname
          and set the same value in the settings object;
        * if no '--DBname', check for a state file in the options.statePath
          and if this exists, read that file and set the DBname and settings
          object;
        * if neither, then check the settings object and set the DBname to
          that;
        * otherwise, failing everything, return an empty string.

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
    if not DBname_get(options):
        return complain(f'''
            Unable to determine which database to use.
            A `--useDB` flag with the database name as
            argument must be specified or alternatively
            be set in the environment as MD_DB or exist
            as a previous configuration state. ''',
            1, messageType.ERROR)
    if not collectionName_get(options):
        return complain(f'''
            Unable to determine the collection within
            the database {C.YELLOW}{DBname_get(options)}{NC} to use.

            A `--useCollection` flag with the collection
            as argument must be specified or alternatively
            be set in the environment as MD_COLLECTION or
            exist as a previous configuration state. ''',
            2,  messageType.ERROR)
    return 0
