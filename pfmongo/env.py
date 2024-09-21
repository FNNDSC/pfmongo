import sys
import pudb
from typing import Callable, Optional
from argparse import Namespace
import asyncio
from asyncio import AbstractEventLoop
from pfmongo.models.dataModel import messageType
from pfmongo.config import settings
from pfmisc import Colors as C
from typing import Literal
import os, sys, json
from pathlib import Path
import appdirs
from pfmongo.models import dataModel, responseModel
from typing import Callable, Optional, Any

try:
    from . import __pkg, __version__
except:
    from pfmongo import __pkg, __version__
from tabulate import tabulate
import click
from io import StringIO
from rich.console import Console

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
LR = C.LIGHT_RED
LB = C.LIGHT_PURPLE
YL = C.YELLOW


class CustomFormatter(click.HelpFormatter):
    def write(self, string):
        super().write(string)


class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        def usage_colorize(usage: str) -> str:
            usage = usage.replace(ctx.command_path, f"{GR}{ctx.command_path}{NC}")
            usage = usage.replace(str(self.name), f"{CY}{self.name}{NC}")
            usage = usage.replace("Usage:", f"{LB}Usage:{NC}")
            return usage

        def options_colorize(options: str) -> str:
            if not "Commands:" in options:
                return options
            l_options: list = options.split("Commands:")[1:][0].split("\n")[1:-1]
            l_cmd: list = [s.split()[0] for s in l_options]
            for cmd in l_cmd:
                options = options.replace(cmd, f"{CY}{cmd}{NC}", 1)
            return options

        # Custom formatting logic for group help
        oformatter: CustomFormatter = CustomFormatter()
        uformatter: CustomFormatter = CustomFormatter()
        super().format_options(ctx, oformatter)
        super().format_usage(ctx, uformatter)
        usage: str = usage_colorize(uformatter.getvalue())
        options: str = options_colorize(oformatter.getvalue())
        click.echo(tabulate_message(str(self.help), usage.strip()))
        click.echo(options)


class CustomCommand(click.Command):
    def format_help(self, ctx, formatter):
        def usage_colorize(usage: str) -> str:
            usage = usage.replace(ctx.command_path, f"{GR}{ctx.command_path}{NC}")
            usage = usage.replace(str(self.name), f"{CY}{self.name}{NC}")
            usage = usage.replace("Usage:", f"{LB}Usage:{NC}")
            return usage

        def options_colorize(options: str) -> str:
            if not "Commands:" in options:
                return options
            l_options: list = options.split("Commands:")[1:][0].split("\n")[1:-1]
            l_cmd: list = [s.split()[0] for s in l_options]
            for cmd in l_cmd:
                options = options.replace(cmd, f"{CY}{cmd}{NC}", 1)
            return options

        # Custom formatting logic for group help
        oformatter: CustomFormatter = CustomFormatter()
        uformatter: CustomFormatter = CustomFormatter()
        super().format_options(ctx, oformatter)
        super().format_usage(ctx, uformatter)
        usage: str = usage_colorize(uformatter.getvalue())
        options: str = options_colorize(oformatter.getvalue())
        click.echo(tabulate_message(str(self.help), usage.strip()))
        click.echo(options)


def tabulate_message(message: str, title: str = "") -> str:
    lines = [[line] for line in message.split("\n")]
    table = tabulate(lines, headers=[f"{title}"], tablefmt="fancy_outline")
    return table


def sprint_multi(string: str, length: int) -> str:
    """
    split a string into several strings of len <length>
    """
    multiline: str = ""
    for i in range(0, len(string), length):
        multiline += string[i : i + length] + "\n"
    return multiline


def complain(message: str, code: int, level: messageType = messageType.INFO) -> int:
    """
    Generate a "complaint" with a message, code, and info level

    :param message: the message
    :param code: the complaint code
    :param level: the type of complaint
    :return: a complaint code
    """
    match level:
        case messageType.ERROR:
            CL = C.RED
        case messageType.INFO:
            CL = C.CYAN
    if settings.appsettings.noComplain:
        return code
    if settings.appsettings.logging == dataModel.loggingType.CONSOLE:
        if message:
            print(tabulate_message(message, f"{CL}{level.name}{NC}"))
    else:
        print(f'{{"level": "{level.name}"}}')
        # pudb.set_trace()
        if message:
            print(f'{{"message": "{to_singleLine(message)}"}}')
    return code


def to_singleLine(message: str) -> str:
    return message.replace("\n", " ")


def URI_sanitize(URI: str) -> str:
    return URI.replace(":", "-").replace("/", "")


def stateDir_get() -> Path:
    return Path(appdirs.user_config_dir(appname=__pkg.name))


def session_config(baseDir: Path) -> Path:
    URI: str = URI_sanitize(settings.mongosettings.MD_URI)
    return baseDir / Path("_MONGO_" + URI)


def sessionUser_notSet() -> int:
    if not settings.mongosettings.MD_sessionUser:
        return complain(
            f"""
                An 'MD_sessionUser' has not been specified in the environment.
                This variable denotes the "name" of a current user of the service
                and is used to store user specific state data.

                Please set with:

                        export {GR}MD_SESSIONUSER{NC}={CY}yourName{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return 0


def response_exitCode(
    var: (
        responseModel.databaseDesc
        | responseModel.collectionDesc
        | responseModel.showAllDBusage
        | responseModel.showAllcollectionsUsage
        | responseModel.DocumentAddUsage
        | responseModel.DocumentGetUsage
        | responseModel.DocumentDeleteUsage
        | responseModel.DocumentSearchUsage
        | responseModel.DocumentListUsage
        | responseModel.dbDeleteUsage
        | responseModel.CollectionDeleteUsage
    ),
) -> int:
    exitCode: int = 0
    match var:
        case responseModel.databaseDesc() | responseModel.collectionDesc():
            exitCode = 0 if var.info.connected else 100
        case responseModel.showAllDBusage():
            exitCode = 0 if var.status else 101
        case responseModel.showAllcollectionsUsage():
            exitCode = 0 if var.status else 102
        case responseModel.DocumentAddUsage():
            exitCode = 0 if var.status else 103
        case responseModel.DocumentGetUsage():
            exitCode = 0 if var.status else 104
        case responseModel.DocumentDeleteUsage():
            exitCode = 0 if var.status else 105
        case responseModel.DocumentSearchUsage():
            exitCode = 0 if var.status else 106
        case responseModel.DocumentListUsage():
            exitCode = 0 if var.status else 107
        case responseModel.dbDeleteUsage():
            exitCode = 0 if var.status else 108
        case responseModel.CollectionDeleteUsage():
            exitCode = 0 if var.status else 109
    return exitCode


def databaseOrCollectionDesc_message(
    var: responseModel.databaseDesc | responseModel.collectionDesc,
) -> str:
    message: str = ""
    message = (
        f'Successfully connected {var.otype} to "{var.name}"'
        if var.info.connected
        else f'Could not connect to mongo {var.otype}: "{var.name}"'
    )
    return message


def documentAddUsage_message(var: responseModel.DocumentAddUsage) -> str:
    message: str = ""
    name: str = ""
    try:
        name = var.document["_id"]
    except KeyError:
        name = var.documentName
    db: str = var.collection.databaseName
    col: str = var.collection.name
    size: int = 0
    if "_size" in var.document:
        size = var.document["_size"]
    message = (
        f'Successfully added "{name}" (size {size}) to "{db}/{col}"'
        if var.status
        else f'Could not add "{name}" (size {size}) to "{db}/{col}"'
    )
    return message


def documentGetUsage_message(var: responseModel.DocumentGetUsage) -> str:
    # pudb.set_trace()
    message: str = ""
    name: str = var.documentName
    db: str = var.collection.databaseName
    col: str = var.collection.name
    size: int = 0
    if "_size" in var.document:
        size = var.document["_size"]
    message = (
        f"{json.dumps(var.document)}"
        if var.status
        else f'Could not get "{name}" (size {size}) from "{db}/{col}"'
    )
    return message


def documentDeleteUsage_message(var: responseModel.DocumentDeleteUsage) -> str:
    message: str = ""
    name: str = var.documentName
    db: str = var.collection.databaseName
    col: str = var.collection.name
    size: int = 0
    message = (
        f'Successfully deleted "{name}" from "{db}/{col}"'
        if var.status
        else f'Could not delete "{name}" from "{db}/{col}"'
    )
    return message


def documentSearchUsage_message(var: responseModel.DocumentSearchUsage) -> str:
    message: str = ""
    message = f"{var.documentList}" if var.status else ""
    return message


def documentListUsage_message(var: responseModel.DocumentListUsage) -> str:
    message: str = ""
    message = f"{var.documentList}" if var.status else ""
    return message


def showAllDBusage_message(var: responseModel.showAllDBusage) -> str:
    message: str = ""
    message = f"{var.databaseNames}" if var.status else ""
    return message


def showAllcollectionsUsage_message(var: responseModel.showAllcollectionsUsage) -> str:
    message: str = ""
    message = f"{var.collectionNames}" if var.status else ""
    return message


def dbDeleteUsage_message(var: responseModel.dbDeleteUsage) -> str:
    message: str = ""
    message = (
        f'Successfully deleted database "{var.dbName}"'
        if var.status
        else f'Could not delete database "{var.dbName}"'
    )
    return message


def collectionDeleteUsage_message(var: responseModel.CollectionDeleteUsage) -> str:
    message: str = ""
    message = (
        f'Successfully deleted collection "{var.collectionName}"'
        if var.status
        else f'Could not delete collection "{var.collectionName}"'
    )
    return message


def response_messageDesc(
    var: (
        responseModel.databaseDesc
        | responseModel.collectionDesc
        | responseModel.showAllDBusage
        | responseModel.showAllcollectionsUsage
        | responseModel.DocumentAddUsage
        | responseModel.DocumentGetUsage
        | responseModel.DocumentDeleteUsage
        | responseModel.DocumentSearchUsage
        | responseModel.DocumentListUsage
        | responseModel.dbDeleteUsage
        | responseModel.CollectionDeleteUsage
    ),
) -> str:
    message: str = ""
    match var:
        case responseModel.databaseDesc() | responseModel.collectionDesc():
            message = databaseOrCollectionDesc_message(var)
        case responseModel.DocumentAddUsage():
            message = documentAddUsage_message(var)
        case responseModel.DocumentGetUsage():
            message = documentGetUsage_message(var)
        case responseModel.DocumentDeleteUsage():
            message = documentDeleteUsage_message(var)
        case responseModel.DocumentSearchUsage():
            message = documentSearchUsage_message(var)
        case responseModel.showAllDBusage():
            message = showAllDBusage_message(var)
        case responseModel.showAllcollectionsUsage():
            message = showAllcollectionsUsage_message(var)
        case responseModel.DocumentListUsage():
            message = documentListUsage_message(var)
        case responseModel.dbDeleteUsage():
            message = dbDeleteUsage_message(var)
        case responseModel.CollectionDeleteUsage():
            message = collectionDeleteUsage_message(var)
    return message


def connectDB_failureCheck(
    connection: responseModel.databaseDesc,
) -> responseModel.databaseDesc:
    if not connection.info.connected:
        complain(
            f"""
                A database connection error has occured. This typically means
                that the mongo DB service has either not been started or has
                not been specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}

                Alternatively, check the mongo service credentials:

                        {GR}export {CY}MD_USERNAME=<user>{NC} && \\
                        {GR}export {CY}MD_PASSWORD=<password>{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return connection


def connectCollection_failureCheck(
    connection: responseModel.collectionDesc,
) -> responseModel.collectionDesc:
    if not connection.info.connected:
        complain(
            f"""
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
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return connection


def showAllcollections_failureCheck(
    usage: responseModel.showAllcollectionsUsage,
) -> responseModel.showAllcollectionsUsage:
    if not usage.info.connected:
        complain(
            f"""
                Unable to show all the collections in the database. This typically means
                that the mongo DB service has either not been started or has not been
                specified correctly, or has incorrect credentialling, or other issues.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return usage


def showAllDBUsage_failureCheck(
    usage: responseModel.showAllDBusage,
) -> responseModel.showAllDBusage:
    if not usage.info.connected:
        complain(
            f"""
                Unable to show all databases in the server. This typically means
                that the mongo DB service has either not been started or has not been
                specified correctly, or has incorrect credentialling, or other issues.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return usage


def usage_failureCheck(
    usage: responseModel.databaseNamesUsage | responseModel.collectionNamesUsage,
) -> responseModel.databaseNamesUsage | responseModel.collectionNamesUsage:
    if not usage.info.connected:
        complain(
            f"""
                A usage error has occured. This typically means that the
                mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    return usage


def addDocument_failureCheck(
    usage: responseModel.DocumentAddUsage,
) -> responseModel.DocumentAddUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    if not usage.status:
        complain(
            f"""
                A document add usage error has occured, reported as:

                {LR}{sprint_multi(usage.resp['error'], 65)}{NC}

                This typically means that a duplicate 'id' has been specified.
                Please check the value of any

                    {CY}--id {GR}<value>{NC}

                 in the {GR}add{NC} subcommand.

                 {CY}{usage.resp['database']}{NC}/{GR}{usage.resp['collection']}{NC}/{LR}{usage.documentName}{NC}

                 If this is a "hash" duplication, it means the document content being uploaded  
                 _already_ exists in the database, even if a different 'id' is being specified.
                 If you want to force upload, use a '--noHashing' flag. 

                """,
            6,
            dataModel.messageType.ERROR,
        )

    return usage


def deleteDocument_failureCheck(
    usage: responseModel.DocumentDeleteUsage,
) -> responseModel.DocumentDeleteUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A document delete error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            5,
            dataModel.messageType.ERROR,
        )
    if not usage.status:
        complain(
            f"""
                A document {YL}delete{NC} usage error has occured. This typically means
                that the passed {CY}id{NC} was not found in the database/collection of
                 {GR}{usage.collection.databaseName}/{usage.collection.name}{NC}

                Please check that

                    {CY}--id {GR}{usage.documentName}{NC}

                in the {YL}delete{NC} subcommand is valid and try again.
                """,
            6,
            dataModel.messageType.ERROR,
        )

    return usage


def deleteDB_failureCheck(
    usage: responseModel.dbDeleteUsage,
) -> responseModel.dbDeleteUsage:
    # pudb.set_trace()
    if not usage.db.info.connected:
        complain(
            f"""
                A db deletion error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Alternatively, the database "{usage.dbName}" does not exist.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            7,
            dataModel.messageType.ERROR,
        )
    elif not usage.status:
        complain(
            f"""
                A database delete usage error has occured. Perhaps the database does not exist?
                """,
            8,
            dataModel.messageType.ERROR,
        )
    return usage


def deleteCollection_failureCheck(
    usage: responseModel.CollectionDeleteUsage,
) -> responseModel.CollectionDeleteUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A collection deletion error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Alternatively, the collection "{usage.collectionName}" does not exist.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            7,
            dataModel.messageType.ERROR,
        )
    elif not usage.status:
        complain(
            f"""
                A collection delete usage error has occured in the monogo deletion call.
                """,
            8,
            dataModel.messageType.ERROR,
        )
    return usage


def listDocument_failureCheck(
    usage: responseModel.DocumentListUsage,
) -> responseModel.DocumentListUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            7,
            dataModel.messageType.ERROR,
        )
    if not usage.status:
        complain(
            f"""
                A document list usage error has occured. This typically means that
                a non existant search query field has been specified. Please check
                the value of any

                    {CY}--field {GR}<value>{NC}

                 in the {GR}list{NC} subcommand.
                """,
            8,
            dataModel.messageType.ERROR,
        )

    return usage


def getDocument_failureCheck(
    usage: responseModel.DocumentGetUsage,
) -> responseModel.DocumentGetUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            7,
            dataModel.messageType.ERROR,
        )
    if not usage.status:
        complain(
            f"""
                A document list get error has occured. This typically means that
                no document in the collection had a matching id term. Please check
                the value of any

                    {CY}--id {GR}<value>{NC}

                 in the {GR}get{NC} subcommand.
                """,
            8,
            dataModel.messageType.ERROR,
        )

    return usage


def searchDocument_failureCheck(
    usage: responseModel.DocumentSearchUsage,
) -> responseModel.DocumentSearchUsage:
    # pudb.set_trace()
    if not usage.collection.info.connected:
        complain(
            f"""
                A document add usage error has occured. This typically means that
                the mongo DB service has either not been started or has not been
                specified correctly.

                Please check the service settings. Usually you might just
                need to start the monogo service with:

                        {GR}docker-compose{NC} {CY}up{NC}
                """,
            7,
            dataModel.messageType.ERROR,
        )
    if not usage.status:
        complain(
            f"""
                A document search usage error has occured. This typically means that
                a non existant search query field has been specified. Please check
                the value of any

                    {CY}--field {GR}<value>{NC}

                 in the {GR}search{NC} subcommand.
                """,
            8,
            dataModel.messageType.ERROR,
        )

    return usage


def env_statePathSet(options: Namespace) -> bool:
    """
    Check/set a path to contain state/persistent data, typically the
    database name and collection within that database.

    The value is set in the options.statePath, and the return value
    indicates failure/success.

    :param options: the set of options
    :return: 0 -- success, non-zero -- failure
    """
    options.thisSession = session_config(stateDir_get())
    if sessionUser_notSet():
        return False
    options.sessionUser = settings.mongosettings.MD_sessionUser
    options.statePath = options.thisSession / options.sessionUser
    if not options.statePath.exists():
        options.statePath.mkdir(parents=True, exist_ok=True)
    return True


def DB_stateFileResolve(options: Namespace) -> Path:
    return options.statePath / Path(settings.mongosettings.stateDBname)


def collection_stateFileResolve(options: Namespace) -> Path:
    return options.statePath / Path(settings.mongosettings.stateColname)


def DBname_stateFileRead(options: Namespace) -> str:
    contents: str = ""
    statefile: Path = DB_stateFileResolve(options)
    if statefile.exists():
        contents = statefile.read_text()
    return contents


def DBname_stateFileSave(options: Namespace, contents: str) -> str:
    statefile: Path = DB_stateFileResolve(options)
    statefile.write_text(contents)
    return contents


def collectionName_stateFileRead(options: Namespace) -> str:
    contents: str = ""
    statefile: Path = collection_stateFileResolve(options)
    if statefile.exists():
        contents = statefile.read_text()
    return contents


def collectionName_stateFileSave(options: Namespace, contents: str) -> str:
    statefile: Path = collection_stateFileResolve(options)
    statefile.write_text(contents)
    return contents


def stateFileSave(
    options: Namespace, contents: str, f_stateFileResolve: Callable[[Namespace], Path]
) -> str:
    statefile: Path = f_stateFileResolve(options)
    statefile.write_text(contents)
    return contents


def stateFileRead(
    options: Namespace, f_stateFileResolve: Callable[[Namespace], Path]
) -> str:
    contents: str = ""
    statefile: Path = f_stateFileResolve(options)
    if statefile.exists():
        contents = statefile.read_text()
    return contents


def collectionName_get(options: Namespace) -> str:
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
        collectionName: str = collectionName_stateFileRead(options)
        if collectionName:
            options.collectionName = collectionName
            settings.mongosettings.MD_COLLECTION = options.DBname
    # if not options.collectionName:
    #     options.collectionName  = settings.mongosettings.MD_COLLECTION
    return options.collectionName


def DBname_get(options: Namespace) -> str:
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
        settings.mongosettings.MD_DB = options.DBname
        DBname_stateFileSave(options, options.DBname)
    if not options.DBname:
        DBname: str = DBname_stateFileRead(options)
        if DBname:
            options.DBname = DBname
            settings.mongosettings.MD_DB = options.DBname
    # if not options.DBname:
    #     options.DBname                  = settings.mongosettings.MD_DB
    return options.DBname


def env_failCheck(options: Namespace) -> int:
    if "--help" in sys.argv:
        return 0
    if not DBname_get(options):
        return complain(
            f"""
            Unable to determine which database to use.

            No resolution method was successful. Resolutions include:
                * a {GR}--useDB {YL}<database>{NC} CLI key/value pair
                * an appropriate MD_DB environment variable
                * a previous CLI {YL}database{NC} subcommand
                * an appropriate CLI {CY}cd {YL}/<database>{NC}
            """,
            1,
            messageType.ERROR,
        )
    if not collectionName_get(options):
        return complain(
            f"""
            Unable to determine the collection within
            the database {C.YELLOW}{DBname_get(options)}{NC} to use.

            A `--useCollection` flag with the collection
            as argument must be specified or alternatively
            be set in the environment as MD_COLLECTION or
            exist as a previous configuration state. """,
            2,
            messageType.ERROR,
        )
    return 0
