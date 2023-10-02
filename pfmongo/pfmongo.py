# Turn off all logging for modules in this libary.
import logging

logging.disable(logging.CRITICAL)

# System imports
import      os
import      sys
import      getpass
import      argparse
import      json
import      pprint
import      csv
import      logging
import      datetime

import      asyncio
import      aiohttp
from        aiohttp             import ClientResponse

from        argparse            import  Namespace, ArgumentParser
from        argparse            import  RawTextHelpFormatter
from        loguru              import  logger

from        pathlib             import  Path
from        pfmisc              import  Colors as C
import      pudb
from        typing              import Any, Callable, Optional
from        pydantic            import HttpUrl

from        pfmongo.config      import settings
from        pfmongo.db          import pfdb
from        pfmongo.models      import responseModel
from        pfmongo             import env

#try:
#    from        config          import settings
#    from        db              import pfdb
#    from        models          import responseModel
#except:
#    from        .config         import settings
#    from        .db             import pfdb
#    from        .models         import responseModel

from click.formatting           import wrap_text

NC              = C.NO_COLOUR
YL              = C.YELLOW
GR              = C.GREEN
CY              = C.CYAN
LOG             = logger.debug
logger_format   = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.add(sys.stderr, format=logger_format)

package_description:str = f"""
                        {YL}pfmongo{NC} -- mongo for rest of us.

    This `project` is a somewhat ideosyncratic class interface to a mongodb.
    It is both a CLI client and supporting python module, following the "pf"
    (see elsewhere) design pattern.

    The basic idea is to provide a class-based set of operations to simplify
    working with data (documents) in a mongodb. For added happiness, a "file
    system-y" metaphor complete with supporting commands that present the
    database as a file system is also provided.

    From the CLI, subcommands are organized into three main groupings:

        {GR}fs{NC} for 'filesystem' type commands,
        {GR}database{NC} for 'database' type commands,
        {GR}collection{NC} for 'collection' type commands

    Use {YL}pfmongo {GR}<grouping> {CY}--help{NC} for <grouping> specific
    help. For example

        {YL}pfmongo {GR}fs {CY}--help{NC}

    for help on the file system commands.

"""

package_coreDescription:str = f'''
    {YL}pfmongo{NC} supports some core CLI arguments that are used to specify
    the general operation of the program, specifically the mongo database to
    use and the collection within that database to access.

    These can also be set with CLI and are specified _before_ the sub command
    to use.

    Additionally, a simple --version can also be specified here.
'''

package_CLIself = '''
        --useDB <DBname>                                                        \\
        --useCollection <collectionName>                                        \\
        [--man]                                                                 \\
        [--version]'''

package_argSynopsisSelf = f"""
        {YL}[--useDB <DBname>]{NC}
        Use the data base called <DBname>.

        {YL}[--useCollection <collectionName>]{NC}
        Use the collection called <collectionName>.

        {YL}[--man]{NC}
        If specified, print this help/man page.

        {YL}[--version]{NC}
        If specified, print app name/version.
"""

package_CLIfull             = package_CLIself
package_CLIDS               = package_CLIself
package_argsSynopsisFull    = package_argSynopsisSelf
package_argsSynopsisDS      = package_argSynopsisSelf

def parser_setup(desc:str, add_help:bool = True) -> ArgumentParser:
    parserSelf = ArgumentParser(
                description         = desc,
                formatter_class     = RawTextHelpFormatter,
                add_help            = add_help
            )

    parserSelf.add_argument("--monogdbinit",
        help    = "JSON formatted file containing mongodb initialization",
        dest    = 'mongodbinit',
        default = '')

    parserSelf.add_argument("--useHashes",
        help    = "add hashes to inserted documents",
        dest    = 'useHashes',
        default = False,
        action  = 'store_true')

    parserSelf.add_argument("--noDuplicates",
        help    = "do not allow duplicate (hashed) documents",
        dest    = 'noDuplicates',
        default = False,
        action  = 'store_true')

    parserSelf.add_argument("--version",
        help    = "print name and version",
        dest    = 'version',
        default = False,
        action  = 'store_true')

    parserSelf.add_argument("--man",
        help    = "print man page",
        dest    = 'man',
        default = False,
        action  = 'store_true')

    parserSelf.add_argument("--useDB",
        help    = "use the named data base",
        dest    = 'DBname',
        default = '')

    parserSelf.add_argument("--useCollection",
        help    = "use the named collection",
        dest    = 'collectionName',
        default = '')

#    parserSelf.add_argument("--addDocument",
#                    help    = "add the contents of the json formatted file",
#                    dest    = 'addDocument',
#                    default = '')
#
#    parserSelf.add_argument("--searchOn",
#                    help    = "search on the passed search token",
#                    dest    = 'searchExp',
#                    default = '')
#
    return parserSelf

def parser_interpret(parser, args) -> tuple:
    """
    Interpret the list space of *args, or sys.argv[1:] if
    *args is empty
    """
    if args:
        args, unknown    = parser.parse_known_args(args)
    else:
        args, unknown    = parser.parse_known_args(sys.argv[1:])
    return args, unknown

def parser_JSONinterpret(parser, d_JSONargs) -> tuple:
    """
    Interpret a JSON dictionary in lieu of CLI.

    For each <key>:<value> in the d_JSONargs, append to
    list two strings ["--<key>", "<value>"] and then
    argparse.
    """
    l_args  = []
    for k, v in d_JSONargs.items():
        if type(v) == type(True):
            if v: l_args.append('--%s' % k)
            continue
        l_args.append('--%s' % k)
        l_args.append('%s' % v)
    return parser_interpret(parser, l_args)

def date_toUNIX(str_date:str) -> int:
    ret:int     = 0
    try:
        date_obj:datetime.datetime  = datetime.datetime.strptime(
                                            str_date, "%Y-%m-%d"
                                    )
        ret                         = int(date_obj.timestamp())
    except:
        pass
    return ret

def responseData_build(d_mongoresp:dict, message:str = "") \
    -> responseModel.mongodbResponse:
    d_resp:responseModel.mongodbResponse \
                    = responseModel.mongodbResponse()
    d_resp.status   = d_mongoresp['status']
    d_resp.response = d_mongoresp
    d_resp.message  = message
    return d_resp

class Pfmongo:
    """

    A class that provides a python API for interacting with a mongodb.

    """

    def  __init__(self, args, **kwargs) -> None:
        self.args:Namespace             = Namespace()
        if type(args) is dict:
            parser:ArgumentParser       = parser_setup('Setup client using dict')
            self.args, extra            = parser_JSONinterpret(parser, args)
        if type(args) is Namespace:
            self.args                   = args

        # attach a comms API to the mongo db
        self.dbAPI:pfdb.mongoDB         = pfdb.mongoDB(
                                            settings    = settings.mongosettings,
                                            args        = self.args
                                        )

        self.responseData:responseModel.mongodbResponse = \
                responseModel.mongodbResponse()
        self.exitCode:int               = 1

    def jsonFile_intoDictRead(self) -> dict[bool,dict]:
        d_json:dict     = {
            'status':   False,
            'data':     {}
        }
        try:
            f = open(self.args.addDocument)
            d_json['data']      = json.load(f)
            d_json['status']    = True
        except Exception as e:
            d_json['data']      = str(e)
        return d_json

    def responseData_logConnection(
            self,
            connection: responseModel.databaseDesc |\
                        responseModel.collectionDesc
    ) -> responseModel.mongodbResponse:
        self.responseData   = responseData_build(
            {
                'status':   connection.info.connected,
                'connect':  connection
            }, self.connect_message(connection)
        )
        return self.responseData

    def responseData_logUsage(
            self,
            usage:  responseModel.databaseNamesUsage    |
                    responseModel.collectionNamesUsage
    ) -> responseModel.mongodbResponse:
        self.responseData   = responseData_build(
            {
                'status':   usage.info.connected,
                'connect':  usage
            }, self.usage_message(usage)
        )
        return self.responseData

    async def showAllDB(self) -> responseModel.databaseNamesUsage:
        allDB:responseModel.databaseNamesUsage = \
                await self.dbAPI.database_names_get()
        self.responseData   = self.responseData_logUsage(allDB)
        return allDB

    async def showAllCollections(self) \
    -> responseModel.collectionNamesUsage|responseModel.databaseNamesUsage:
        allCollections:responseModel.collectionNamesUsage   = \
           responseModel.collectionNamesUsage()
        connectDB:responseModel.databaseDesc    = \
                await self.connectDB(env.DBname_get(self.args))
        if not connectDB.info.connected:
            databaseUsageFail:responseModel.databaseNamesUsage = \
                                responseModel.databaseNamesUsage()
            databaseUsageFail.info  = connectDB.info
            return databaseUsageFail
        allCollections      = await self.dbAPI.collection_names_get()
        allCollections.info = connectDB.info
        self.responseData   = self.responseData_logUsage(allCollections)
        return allCollections

    async def documentAdd(self):
        d_json:dict         = self.jsonFile_intoDictRead()
        if d_json['status']:
            d_resp:dict     = await self.dbAPI.insert_one(
                                intoCollection  = self.args.collectionName,
                                document        = d_json['data']
                        )
            pudb.set_trace()
            self.responseData       = responseData_build(
                                        d_resp,
                                        'Document inserted successfully'\
                                            if d_resp['status'] else    \
                                        'Document insert failure'
                                    )

    def usage_message(
            self,
            usage:  responseModel.databaseNamesUsage    |
                    responseModel.collectionNamesUsage
    ) -> str:
        message:str         = ""
        if not usage.info.connected:
            message         = f'Usage error while {usage.otype}'
            self.exitCode   = 10
        else:
            message         = f'Success while {usage.otype}'
            self.exitCode   = 0
        return message

    def connect_message(
            self,
            connect:responseModel.databaseDesc|responseModel.collectionDesc
    ) -> str:
        message:str         = ""
        if not connect.info.connected:
            message         = \
                f'Could not connect to mongo {connect.otype}: "{connect.name}"'
            self.exitCode   = 10
        else:
            message         = \
                f'Connected to mongo {connect.otype}: "{connect.name}"'
            self.exitCode   = 0
        return message

    async def connectDB(self, DBname:str) -> responseModel.databaseDesc:
        connect:responseModel.databaseDesc  = await self.dbAPI.connect(DBname)
        self.responseData   = self.responseData_logConnection(connect)
        if self.responseData.response['status']:
            env.stateFileSave(self.args, DBname, env.DB_stateFileResolve)
        return connect

    async def connectCollection(self, collectionName:str) \
    -> responseModel.collectionDesc|responseModel.databaseDesc:
        connectDB:responseModel.databaseDesc    = \
                await self.connectDB(env.DBname_get(self.args))
        if not connectDB.info.connected:
            return connectDB
        connectCol:responseModel.collectionDesc = \
                await self.dbAPI.collection_connect(collectionName)
        self.responseData   = self.responseData_logConnection(connectCol)
        # pudb.set_trace()
        if self.responseData.response['status']:
            env.stateFileSave(
                    self.args,
                    collectionName,
                    env.collection_stateFileResolve
            )
        return connectCol

    async def service(self) -> None:
        pudb.set_trace()

        if not hasattr(self.args, 'do'):
            return

        match(self.args.do):
            case 'showAllDB':
                env.usage_failureCheck(
                    await self.showAllDB()
                )
            case 'showAllCollections':
                env.usage_failureCheck(
                    await self.showAllCollections()
                )
            case 'connectDB':
                env.connection_failureCheck(
                    await self.connectDB(self.args.argument)
                )
            case 'connectCollection':
                env.connection_failureCheck(
                    await self.connectCollection(self.args.argument)
                )
            case 'addDocument':
                await self.documentAdd()
