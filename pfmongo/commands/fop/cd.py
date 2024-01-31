from    argparse    import Namespace
import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel, fsModel
from    pathlib         import  Path
import  pudb

from    pfmongo.commands.document   import showAll as doc
from    pfmongo.commands.state      import showAll as state
from    pfmongo.commands.database   import showAll as mdb
from    pfmongo.commands.database   import connect as dbconnect
from    pfmongo.commands.collection import showAll as col
from    pfmongo.commands.collection import connect as colconnect
import  pfmongo.commands.smash                     as smash
import  copy

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

def options_add(path:str, options:Namespace) -> Namespace:
    localoptions            = copy.deepcopy(options)
    # localoptions.beQuiet    = True
    localoptions.do         = 'cd'
    localoptions.path       = Path(path)
    return localoptions

def fullPath_resolve(options:Namespace) -> Namespace:
    if options.path.is_absolute(): return options
    options.path = smash.cwd(options) / options.path
    return options

def db_isListed(db:str, options:Namespace) -> fsModel.cdResponse:
    fsPath:fsModel.cdResponse   = fsModel.cdResponse()
    if db not in mdb.showAll_asModel(driver.settmp(options,[
                                                    {'do': 'showAllDB'}
                                                    ])).message:
        fsPath.error    = f"database '{db}' not in mongo"
        fsPath.code     = 2


def path_connect(options:Namespace) -> fsModel.cdResponse:
    path:Path   = options.path
    # need to track cwd
    fsPath:fsModel.cdResponse = fsModel.cdResponse()
    if len(path.parents) > 2:
        fsPath.error    = "Path too long"
        fsPath.code     = 1
        return fsPath
    (db, collection)    = path_to_dbCol(options)
    fsPath.path         = options.path
    if db not in mdb.showAll_asModel(driver.settmp(options,[
                                                    {'do': 'showAllDB'}
                                                    ])).message:
        fsPath.error    = f"database '{db}' not in mongo"
        fsPath.code     = 2
        return fsPath
    if (dbConnectFail:=dbconnect.connectTo_asInt(dbconnect.options_add(db, options))):
        fsPath.error    = f"could not connect to database '{db}'"
        fsPath.code     = 3
        return fsPath
    if collection not in col.showAll_asModel(options).message:
        fsPath.error    = f"collection '{collection}' not in database '{db}'"
        fsPath.code     = 4
    if (colCollectFail:=colconnect.connectTo_asInt(colconnect.options_add(collection, options))):
        fsPath.error    = f"could not connect to collection '{collection}'"
        fsPath.code     = 5
        return fsPath
    fsPath.status   = True
    fsPath.mesasge  = f"successfully changed path to {path}"
    fsPath.code     = 0
    return fsPath

def path_to_dbCol(options:Namespace) -> tuple:
    # if not path_isValid(options, path):
    #     return ()
    path:Path       = options.path
    db:str          = ""
    collection:str  = ""
    match len(path.parts):
        case _ if len(path.parts) >=2:
            (root, db)  = path.parts
        case _ if len(path.parts) > 2:
            (root, db, collection) = path.parts
    return (db, collection)

def path_lengthOK(options:Namespace) -> bool:
    return True if len(options.path.parents.parts == 2) else False

def path_set(options:Namespace, path:Path) -> Namespace:
    dbname:str      = ""
    collection:str  = ""
    match len(path.parents):
        case _ if len(path.parents) >= 1:
            dbname      = path.parts[1]
        case 2:
            collection  = path.parts[2]
    env.DBname_stateFileSave(options, dbname)
    env.collectionName_stateFileSave(options, collection)
    return driver.settmp(
            options,
            [{'DBname'           : dbname},
             {'collectionName'   : collection}])

def changeDirectory(options:Namespace) -> int:
    options             = fullPath_resolve(options)
    currentpath:Path    = smash.cwd(options)
    if (cdResponse:=path_connect(options)).code:
        print(cdResponse.error)
        # return 1
    # path_set(options, target)
    return cdResponse.code

@click.command(cls = env.CustomCommand, help=f"""
change directory

SYNOPSIS
{CY}cd {YL}<path>{NC}

DESC
The {YL}cd{NC} command "changes directory" within a mongodb between a
<database> level at the root `/` and a collection within a
<database>. Since there are only ever two "directories" in a
mongodb, trees are not especially nested.

""")
@click.argument('path',
                required = True)
@click.pass_context
def cd(ctx:click.Context, path:str) -> int:
    pudb.set_trace()
    return changeDirectory(options_add(path, ctx.obj['options']))
    # target:Path         = fullPath_resolve(options)
    # currentpath:Path    = smash.cwd(options)
    # if (cdResponse:=path_connect(options, target)).code:
    #     print(cdResponse.error)
    #     return 1
    # path_set(options, target)


