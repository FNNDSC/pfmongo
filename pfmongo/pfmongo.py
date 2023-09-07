# Turn off all logging for modules in this libary.
import logging

from pytest import fail

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
from        typing              import Any, Callable
from        pydantic            import HttpUrl

try:
    from        config          import settings
    from        db              import pfdb
    from        models          import responseModel
except:
    from        .config         import settings
    from        .db             import pfdb
    from        .models         import responseModel


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
    {C.YELLOW}pfmongo{C.NO_COLOUR} is a somewhat ideosyncratic class interface to a mongodb. It is
    both a CLI client and supporting python module, following the "pf" (see
    elsewhere) design pattern.

    The basic idea is to provide a class-based set of operations to simplify
    adding and retrieving (and searching) for documents in a mongodb.
"""

package_CLIself = '''
        [--mongodbinit <init.json>]                                             \\
        [--useDB <DBname>]                                                      \\
        [--useCollection <collectionName>]                                      \\
        [--addDocument <document.json>]                                         \\
        [--searchOn <searchString>]                                             \\
        [--man]                                                                 \\
        [--version]'''

package_argSynopsisSelf = f"""
        {C.YELLOW}[--mongodbinit <init.json>]{C.NO_COLOUR}
        The mongodb initialization file.

        {C.YELLOW}[--version]{C.NO_COLOUR}
        If specified, print app name/version.

        {C.YELLOW}[--man]{C.NO_COLOUR}
        If specified, print this help/man page.

        {C.YELLOW}[--useDB <DBname>]{C.NO_COLOUR}
        Use the data base called <DBname>.

        {C.YELLOW}[--useCollection <collectionName>]{C.NO_COLOUR}
        Use the collection called <collectionName>.

        {C.YELLOW}[--addDocument <document.json>]{C.NO_COLOUR}
        Add the <document.json> to the <DBname>/<collectionName>.

        {C.YELLOW}[--searchOn <searchExp>]{C.NO_COLOUR}
        Search for <searchExp> (see below) in the <DBname>/<collectionName>.

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

    parserSelf.add_argument("--version",
                    help    = "print name and version",
                    dest    = 'b_version',
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
                    default = 'pf_defaultDB')

    parserSelf.add_argument("--useCollection",
                    help    = "use the named collection",
                    dest    = 'collectionName',
                    default = 'pf_defaultCollection')

    parserSelf.add_argument("--addDocument",
                    help    = "add the contents of the json formatted file",
                    dest    = 'jsonFile',
                    default = '')

    parserSelf.add_argument("--searchOn",
                    help    = "search on the passed search token",
                    dest    = 'searchExp',
                    default = '')

    return parserSelf

def parser_interpret(parser, *args):
    """
    Interpret the list space of *args, or sys.argv[1:] if
    *args is empty
    """
    if len(args):
        args    = parser.parse_args(*args)
    else:
        args    = parser.parse_args(sys.argv[1:])
    return args

def parser_JSONinterpret(parser, d_JSONargs):
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
        date_obj:datetime.datetime  = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        ret                         = int(date_obj.timestamp())
    except:
        pass
    return ret

class Pfmongo:
    """

    A class that provides a python API for interacting with a monogodb.

    """

    def  __init__(self, args, **kwargs) -> None:

        if type(args) is dict:
            parser:ArgumentParser           = parser_setup('Setup client using dict')
            self.args:Namespace             = parser_JSONinterpret(parser, args)
        if type(args) is Namespace:
            self.args:Namespace             = args

        # attach a comms API to the mongo db
        self.dbAPI:pfdb.mongoDB             = pfdb.mongoDB(
                                                    name     = self.args.DBname,
                                                    settings = settings.mongosettings
                                            )

        # an aiohttp session
        self._session               = aiohttp.ClientSession()
        self.responseData:responseModel.mongodbResponse = responseModel.mongodbResponse()

    async def close(self) -> None:
        await self._session.close()

    def jsonFile_intoDictRead(self) -> dict[bool,dict]:
        d_json:dict     = {
            'status':   False,
            'data':     {}
        }
        try:
            f = open(self.args.jsonFile)
            d_json['data']      = json.load(f)
            d_json['status']    = True
        except Exception as e:
            d_json['data']      = str(e)
        return d_json

    async def service(self) -> None:
        pudb.set_trace()
        d_data:dict             = {}

        self.dbAPI.collection_add(self.args.collectionName)

        if self.args.jsonFile:
            d_json:dict         = self.jsonFile_intoDictRead()
            if d_json['status']:
                self.dbAPI.insert_one(
                        intoCollection  = self.args.collectionName,
                        document        = d_json
                )


#        d_data:sensorModel.persairResponse  = sensorModel.persairResponse()
#
#        if self.args.sensorDataGet:
#            str_history:str     = ""
#            if self.args.asHistory:
#                str_history     = f"/history"
#            if self.args.asHistoryCSV:
#                str_history     = f"/history/csv"
#            d_data  = await self.sensor_dataGet(
#                self.args.sensorDataGet,
#                self.args.fields,
#                str_history
#            )
#        if self.args.sensorAddToGroup:
#            d_data  = await self.sensor_toGroupAdd(
#                self.args.sensorAddToGroup, self.args.usingGroupID
#            )
#        if self.args.sensorsAddFromFile:
#            d_data  = await self.sensors_toGroupFromFile(
#                self.args.usingGroupID, Path(self.args.sensorsAddFromFile)
#            )
#        if self.args.sensorsInGroupList:
#            d_data  = await self.sensors_inGroupGet(
#                self.args.usingGroupID
#            )
#
        # Close this comms session
        await self.close()
        self.responseData   = responseModel.mongodbResponse()

