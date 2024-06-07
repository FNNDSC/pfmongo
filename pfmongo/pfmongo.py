# Turn off all logging for modules in this libary.
import logging

logging.disable(logging.CRITICAL)

# System imports
import sys
import logging
import datetime

from argparse import Namespace, ArgumentParser
from argparse import RawTextHelpFormatter
from loguru import logger

from pfmisc import Colors as C
import pudb
from typing import Any, Callable, Optional

from pfmongo.config import settings
from pfmongo.db import pfdb
from pfmongo.models import responseModel
from pfmongo import env
import copy

NC = C.NO_COLOUR
YL = C.YELLOW
GR = C.GREEN
CY = C.CYAN
PR = C.PURPLE
LOG = logger.debug
logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.add(sys.stderr, format=logger_format)

package_description: str = f"""
                        {YL}pfmongo{NC} -- mongo for rest of us.

    This system is a somewhat ideosyncratic interface to a {PR}mongodb{NC} server.
    It is both a CLI client and supporting python module, following the "pf"
    (see elsewhere) design pattern.

    The basic idea is to provide a subcommand based set of operations to
    simplify working with data (documents) in a {PR}mongodb{NC}.

    For added happiness, a "file system-y" metaphor complete with supporting
    commands that present the database as a file system is also provided.

    In addtion, see the {PR}pfmdb{NC} FastAPI-based system that provides a full
    REST interface to {YL}pfmongo{NC}.

    From the CLI, subcommands are organized the following groupings:

        {GR}fs{NC}          for 'filesystem' type commands,
        {GR}database{NC}    for 'database' type commands,
        {GR}collection{NC}  for 'collection' type commands,
        {GR}document{NC}    for 'document' type commands
        {GR}smash{NC}       the pfmongo REPL 'shell'

    Use {YL}pfmongo {GR}<grouping> {CY}--help{NC} for <grouping> specific help. For example

        {YL}pfmongo {GR}document {CY}--help{NC}

    for help on the {GR}document{NC} contextual commands.

"""

package_coreDescription: str = f"""
    {YL}pfmongo{NC} supports some core CLI arguments that are used to specify
    the general operation of the program, specifically the mongo database to
    use and the collection within that database to access.

    These can also be set with CLI and are specified _before_ the sub command
    to use.

    Additionally, a simple --version can also be specified here.
"""

package_CLIself = """
        [--useDB <DBname>]                                                      \\
        [--useCollection <collectionName>]                                      \\
        [--noHashing]                                                           \\
        [--noDuplicates]                                                        \\
        [--donotFlatten]                                                        \\
        [--noResponseTruncSize]                                                 \\
        [--detailedOutput]                                                      \\
        [--noComplain]                                                          \\
        [--beQuiet]                                                             \\
        [--eventLoopDebug]                                                      \\
        [--responseTruncDepth <depth>]                                          \\
        [--responseTruncSize <size>]                                            \\
        [--man]                                                                 \\
        [--version]"""

package_argSynopsisSelf = f"""
        {YL}[--useDB <DBname>]{NC}
        Use the data base called <DBname>.

        {YL}[--useCollection <collectionName>]{NC}
        Use the collection called <collectionName>.

        {YL}[--noHashing>]{NC}
        If set, do not add payload hashes to documents. By default a hash of
        the document is calculated and added as a field when saved to a
        collection. This hash serves as a "fingerprint" of the document
        assuring _content_ uniqueness.

        {YL}[--noDuplicates]{NC}
        If set, and in combination with --noHashing, will not allow a new
        document with the same hash as an existing one to be saved to a
        collection.

        {YL}[--donotFlatten]{NC}
        If set, do not add a flattened document to a shadow collection. Since
        the interal structure of a document can be complex with nested data
        structures, a "flattened" version of the document is added to a
        "shadow" collection. This flattened version is consulted for quick
        value searching. In other words, flattened documents are internal
        artifacts and a side-effect of adding data to the collection. By
        passing this flag, a flattened version is not created or saved. Note
        that not flattening will severely limit searches!

        {YL}[--noResponseSizeTrunc]{NC}
        If set, do not truncate response returns from pfmongo calls. Note that
        some responses can be "wordy", so only use if strictly needed.

        {YL}[--noComplain]{NC}
        If set, suppress the "complain" messages that typically provide more
        information on error or warning events.

        {YL}[--beQuiet]{NC}
        If set, suppress all output to console. Note that "models" still contain
        data and the contents of the model '.message' is the string that would
        typically have been printed. This option is mostly useful if some other
        process is using pfmongo and wants to prevent pfmongo itself from polluting
        the console.

        {YL}[--detailedOutput]{NC}
        If set, more detailed output result payloads.

        {YL}[--eventLoopDebug]{NC}
        If set, activate a hidden "pudb.set_trace()" in the main event loop.

        {YL}[--responseTruncSize <size>]{NC}
        Set the size limit on a given (nested) set of data in the response from
        the app. You probably won'y need this.

        {YL}[--responseTruncDepth <depth>]{NC}
        Set the depth within a response below which to possibly truncatate on
        response size. You probably won't need this.

        {YL}[--man]{NC}
        If specified, print this help/man page.

        {YL}[--version]{NC}
        If specified, print app name/version.
"""

package_CLIfull = package_CLIself
package_CLIDS = package_CLIself
package_argsSynopsisFull = package_argSynopsisSelf
package_argsSynopsisDS = package_argSynopsisSelf


def parser_setup(desc: str, add_help: bool = True) -> ArgumentParser:
    parserSelf = ArgumentParser(
        description=desc, formatter_class=RawTextHelpFormatter, add_help=add_help
    )

    parserSelf.add_argument(
        "--monogdbinit",
        help="JSON formatted file containing mongodb initialization",
        dest="mongodbinit",
        default="",
    )

    parserSelf.add_argument(
        "--noHashing",
        help="do not add hashes to inserted documents",
        dest="noHashing",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--allowDuplicates",
        help="allow duplicate (hashed) documents",
        dest="allowDuplicates",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--donotFlatten",
        help="do not add shadow 'flattened' collection",
        dest="donotFlatten",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--noResponseTruncSize",
        help="do not truncate responses, even if nested and high data",
        dest="noResponseTruncSize",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--noComplain",
        help="suppress complaint details",
        dest="noComplain",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--beQuiet",
        help="suppress all console output",
        dest="beQuiet",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--detailedOutput",
        help="provide more detailed result payloads",
        dest="detailedOutput",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--eventLoopDebug",
        help="activate a hidden event loop breakpoint",
        dest="eventLoopDebug",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--modelSizesPrint",
        help="on final response, also print internal model size information",
        dest="modelSizesPrint",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--responseTruncSize",
        help="set the cumulative truncation size limit",
        dest="responseTruncSize",
        default="",
    )

    parserSelf.add_argument(
        "--responseTruncDepth",
        help="set the nested depth at which to consider truncation",
        dest="responseTruncDepth",
        default="",
    )

    parserSelf.add_argument(
        "--version",
        help="print name and version",
        dest="version",
        default=False,
        action="store_true",
    )

    parserSelf.add_argument(
        "--man", help="print man page", dest="man", default=False, action="store_true"
    )

    parserSelf.add_argument(
        "--useDB", help="use the named data base", dest="DBname", default=""
    )

    parserSelf.add_argument(
        "--useCollection",
        help="use the named collection",
        dest="collectionName",
        default="",
    )

    return parserSelf


def parser_interpret(parser, args) -> tuple:
    """
    Interpret the list space of *args, or sys.argv[1:] if
    *args is empty
    """
    if args:
        args, unknown = parser.parse_known_args(args)
    else:
        args, unknown = parser.parse_known_args(sys.argv[1:])
    return args, unknown


def parser_JSONinterpret(parser, d_JSONargs) -> tuple:
    """
    Interpret a JSON dictionary in lieu of CLI.

    For each <key>:<value> in the d_JSONargs, append to
    list two strings ["--<key>", "<value>"] and then
    argparse.
    """
    l_args = []
    for k, v in d_JSONargs.items():
        if v.isinstance(bool):
            if v:
                l_args.append("--%s" % k)
            continue
        l_args.append("--%s" % k)
        l_args.append("%s" % v)
    return parser_interpret(parser, l_args)


def options_initialize(override: list[dict] = []) -> Namespace:
    """initialize a set of "options" with defaults"""
    options: Namespace = Namespace()
    parser: ArgumentParser = parser_setup("A client parser for pfmongo", add_help=False)
    options, extra = parser_interpret(parser, [])
    if len(override):
        options = options_set(options, override)
    env.env_statePathSet(options)
    return options


def timenow(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.datetime.now().strftime(fmt)


def date_toUNIX(str_date: str) -> int:
    ret: int = 0
    try:
        date_obj: datetime.datetime = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        ret = int(date_obj.timestamp())
    except Exception as e:
        print(f"{e}")
    return ret


def responseData_build(
    d_mongoresp: dict, message: str = ""
) -> responseModel.mongodbResponse:
    d_resp: responseModel.mongodbResponse = responseModel.mongodbResponse()
    d_resp.status = d_mongoresp["status"]
    d_resp.response = d_mongoresp
    d_resp.message = message
    return d_resp


def options_set(options: Namespace, newkeyvaluepair: list) -> Namespace:
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


class Pfmongo:
    """

    A class that provides a python API for interacting with a mongodb.

    """

    def setup_fromCLI(self) -> None:
        settings.appsettings.allowDuplicates = self.args.allowDuplicates
        settings.appsettings.noHashing = self.args.noHashing
        settings.appsettings.donotFlatten = self.args.donotFlatten
        settings.appsettings.detailedOutput = self.args.detailedOutput
        settings.appsettings.noComplain = self.args.noComplain
        settings.appsettings.eventLoopDebug = self.args.eventLoopDebug
        settings.appsettings.noResponseTruncSize = self.args.noResponseTruncSize
        settings.appsettings.modelSizesPrint = self.args.modelSizesPrint
        settings.appsettings.beQuiet = self.args.beQuiet
        if self.args.responseTruncSize:
            settings.mongosettings.responseTruncSize = self.args.responseTruncSize
        if self.args.responseTruncDepth:
            settings.mongosettings.responseTruncDepth = self.args.responseTruncDepth

    def __init__(self, args, **kwargs) -> None:
        self.args: Namespace = Namespace()
        if isinstance(args, dict):
            parser: ArgumentParser = parser_setup("Setup client using dict")
            self.args, extra = parser_JSONinterpret(parser, args)
        if type(args) is Namespace:
            self.args = args

        # attach a comms API to the mongo db
        self.dbAPI: pfdb.mongoDB = pfdb.mongoDB(
            settings=settings.mongosettings, args=self.args
        )

        self.responseData: responseModel.mongodbResponse = (
            responseModel.mongodbResponse()
        )
        self.exitCode: int = 1
        self.setup_fromCLI()

    def responseData_log(self, data: Any) -> responseModel.mongodbResponse:
        self.exitCode = env.response_exitCode(data)
        self.responseData = responseData_build(
            {"status": data.status, "connect": data}, env.response_messageDesc(data)
        )
        return self.responseData

    async def showAllDB(self) -> responseModel.showAllDBusage:
        self.responseData = self.responseData_log(
            (allDB := await self.dbAPI.database_names_get())
        )
        return allDB

    async def showAllCollections(self) -> responseModel.showAllcollectionsUsage:
        allCollections: responseModel.showAllcollectionsUsage = (
            responseModel.showAllcollectionsUsage()
        )
        if not (
            connectDB := await self.connectDB(env.DBname_get(self.args))
        ).info.connected:
            allCollections.info = connectDB.info
            return allCollections
        allCollections = await self.dbAPI.collection_names_get()
        allCollections.info = connectDB.info
        self.responseData = self.responseData_log(allCollections)
        return allCollections

    async def deleteCollection(
        self, collection: str
    ) -> responseModel.CollectionDeleteUsage:
        collectionDelete: responseModel.CollectionDeleteUsage = (
            responseModel.CollectionDeleteUsage()
        )
        if not (
            connectCol := await self.connectCollection_do(
                env.collectionName_get(self.args)
            )
        ).info.connected:
            collectionDelete.collection = connectCol
            return collectionDelete
        self.responseData_log(
            collectionDelete := await self.dbAPI.collection_delete(collection)
        )
        return collectionDelete

    async def documentAdd(self, d_json: dict) -> responseModel.DocumentAddUsage:
        documentAdd: responseModel.DocumentAddUsage = responseModel.DocumentAddUsage()
        if not (
            connectCol := await self.connectCollection_do(
                env.collectionName_get(self.args)
            )
        ).info.connected:
            documentAdd.collection = connectCol
            return documentAdd
        self.responseData_log(
            documentAdd := await self.dbAPI.insert_one(connectCol, document=d_json)
        )
        return documentAdd

    async def documentDelete(self, id: str) -> responseModel.DocumentDeleteUsage:
        documentDelete: responseModel.DocumentDeleteUsage = (
            responseModel.DocumentDeleteUsage()
        )
        if not (
            connectCol := await self.connectCollection_do(
                env.collectionName_get(self.args)
            )
        ).info.connected:
            documentDelete.collection = connectCol
            return documentDelete
        self.responseData_log(
            documentDelete := await self.dbAPI.delete_one(connectCol, document=id)
        )
        return documentDelete

    async def documentList(self, field: str) -> responseModel.DocumentListUsage:
        documentList: responseModel.DocumentListUsage = (
            responseModel.DocumentListUsage()
        )
        if not (
            connectCol := await self.connectCollection_do(
                env.collectionName_get(self.args)
            )
        ).info.connected:
            documentList.collection = connectCol
            return documentList
        self.responseData_log(
            documentList := await self.dbAPI.listDocs(connectCol, field=field)
        )
        return documentList

    async def documentSearch(
        self, searchFor: list, field: str
    ) -> responseModel.DocumentSearchUsage:
        """search whatever is the contextual collection!"""
        documentList: responseModel.DocumentSearchUsage = (
            responseModel.DocumentSearchUsage()
        )
        collection: str = env.collectionName_get(self.args)
        # if not settings.appsettings.donotFlatten:
        #     collection += settings.mongosettings.flattenSuffix
        if not (
            connectCol := await self.connectCollection_do(collection)
        ).info.connected:
            documentList.collection = connectCol
            return documentList
        self.responseData_log(
            documentList := await self.dbAPI.searchDocs(
                connectCol, searchFor=searchFor, field=field
            )
        )
        # reconnect to non-flat in a thread safe way?
        return documentList

    async def documentGet(self, id: str) -> responseModel.DocumentGetUsage:
        documentGet: responseModel.DocumentGetUsage = responseModel.DocumentGetUsage()
        if not (
            connectCol := await self.connectCollection_do(
                env.collectionName_get(self.args)
            )
        ).info.connected:
            documentGet.collection = connectCol
            return documentGet
        self.responseData_log(
            documentGet := await self.dbAPI.get_one(connectCol, document=id)
        )
        return documentGet

    async def connectDB(self, DBname: str) -> responseModel.databaseDesc:
        connect: responseModel.databaseDesc = responseModel.databaseDesc()
        self.responseData_log((connect := await self.dbAPI.connect(DBname)))
        if self.responseData.response["status"]:
            env.stateFileSave(self.args, DBname, env.DB_stateFileResolve)
        return connect

    async def deleteDB(self, DB: str) -> responseModel.dbDeleteUsage:
        dbDelete: responseModel.dbDeleteUsage = responseModel.dbDeleteUsage()
        if not (
            connectDB := await self.connectDB_do(env.DBname_get(self.args))
        ).info.connected:
            dbDelete.db = connectDB
            return dbDelete
        dbDelete.dbName = DB
        dbDelete.db = connectDB
        self.responseData_log(dbDelete := await self.dbAPI.db_delete(dbDelete))
        return dbDelete

    async def connectCollection(
        self, collectionName: str
    ) -> responseModel.collectionDesc:
        connectCol: responseModel.collectionDesc = responseModel.collectionDesc()
        connectDB: responseModel.databaseDesc = await self.connectDB(
            env.DBname_get(self.args)
        )
        connectCol.database = connectDB
        if not connectDB.info.connected:
            return connectCol
        connectCol = await self.dbAPI.collection_connect(collectionName)
        connectCol.database = connectDB
        self.responseData = self.responseData_log(connectCol)
        # pudb.set_trace()
        if self.responseData.response["status"]:
            env.stateFileSave(
                self.args, collectionName, env.collection_stateFileResolve
            )
            self.args.collectionName = collectionName
        return connectCol

    async def collectionDesc_check(self) -> responseModel.collectionDesc:
        connectCol: responseModel.collectionDesc = responseModel.collectionDesc()
        DBdesc: responseModel.databaseDesc = await self.connectDB(
            env.DBname_get(self.args)
        )

        if not DBdesc.info.connected:
            connectCol.info.error = DBdesc.info.error
            return connectCol
        connectCol = await self.dbAPI.collection_connect(
            env.collectionName_get(self.args)
        )
        self.responseData = self.responseData_log(connectCol)
        if self.responseData.response["status"]:
            env.stateFileSave(
                self.args,
                env.collectionName_get(self.args),
                env.collection_stateFileResolve,
            )
        return connectCol

    async def showAllDB_do(self) -> responseModel.showAllDBusage:
        return env.showAllDBUsage_failureCheck(await self.showAllDB())

    async def showAllCollections_do(self) -> responseModel.showAllcollectionsUsage:
        return env.showAllcollections_failureCheck(await self.showAllCollections())

    async def connectDB_do(self, DBname: str) -> responseModel.databaseDesc:
        return env.connectDB_failureCheck(await self.connectDB(DBname))

    async def connectCollection_do(
        self, collection: str
    ) -> responseModel.collectionDesc:
        return env.connectCollection_failureCheck(
            await self.connectCollection(collection)
        )

    async def addDocument_do(self, document: dict) -> responseModel.DocumentAddUsage:
        return env.addDocument_failureCheck(await self.documentAdd(document))

    async def deleteDocument_do(self, id: str) -> responseModel.DocumentDeleteUsage:
        return env.deleteDocument_failureCheck(await self.documentDelete(id))

    async def deleteCollection_do(
        self, collection: str
    ) -> responseModel.CollectionDeleteUsage:
        return env.deleteCollection_failureCheck(
            await self.deleteCollection(collection)
        )

    async def deleteDB_do(self, DB: str) -> responseModel.dbDeleteUsage:
        return env.deleteDB_failureCheck(await self.deleteDB(DB))

    async def listDocument_do(self, field: str) -> responseModel.DocumentListUsage:
        return env.listDocument_failureCheck(await self.documentList(field))

    async def getDocument_do(self, id: str) -> responseModel.DocumentGetUsage:
        return env.getDocument_failureCheck(await self.documentGet(id))

    async def searchDocument_do(
        self, search: dict
    ) -> responseModel.DocumentSearchUsage:
        return env.searchDocument_failureCheck(
            await self.documentSearch(search["searchFor"], search["field"])
        )

    async def service(self) -> None:
        if settings.appsettings.eventLoopDebug:
            pudb.set_trace()

        if not hasattr(self.args, "do"):
            return

        match self.args.do:
            case "showAllDB":
                await self.showAllDB_do()
            case "showAllCollections":
                await self.showAllCollections_do()
            case "connectDB":
                await self.connectDB_do(self.args.argument)
            case "deleteDB":
                await self.deleteDB_do(self.args.argument)
            case "connectCollection":
                await self.connectCollection_do(self.args.argument)
            case "addDocument":
                await self.addDocument_do(self.args.argument)
            case "deleteDocument":
                await self.deleteDocument_do(self.args.argument)
            case "deleteCollection":
                await self.deleteCollection_do(self.args.argument)
            case "listDocument":
                await self.listDocument_do(self.args.argument)
            case "getDocument":
                await self.getDocument_do(self.args.argument)
            case "searchDocument":
                await self.searchDocument_do(self.args.argument)
