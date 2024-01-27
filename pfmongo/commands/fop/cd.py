from    argparse    import Namespace
import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel, dataModel
from    pathlib         import  Path
import  pudb

from    pfmongo.commands.document   import showAll as doc
from    pfmongo.commands.state      import showAll as state
from    pfmongo.commands.database   import showAll as mdb
from    pfmongo.commands.database   import connect as dbconnect
from    pfmongo.commands.collection import showAll as col
from    pfmongo.commands.collection import connect as colconnect
import  pfmongo.commands.smash                   as smash

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

def fullPath_resolve(options:Namespace, path:Path) -> Path:
    if path.is_absolute(): return path
    path = smash.cwd(options) / path
    return path

def path_isValid(options:Namespace, path:Path) -> dataModel.fsPath:
    # need to track cwd
    fsPath:dataModel.fsPath     = dataModel.fsPath()
    if len(path.parents) > 2:
        fsPath.error    = "Path too long"
        return fsPath
    (db, collection)    = path_parts(options, path)
    if db not in mdb.showAll_asModel(options).message:
        fsPath.error    = f"database {db} not in mongo"
        return fsPath
    if (dbConnectFail:=dbconnect.connectTo_asInt(dbconnect.options_add(db, options))):
        fsPath.error    = f"could not connect to database {db}"
        return fsPath
    if collection not in col.showAll_asModel(options).message:
        fsPath.error    = f"collection {collection} not in database {db}"
    if (colCollectFail:=colconnect.connectTo_asInt(colconnect.options_add(collection, options))):
        fsPath.error    = "could not connect to collection"
        return fsPath
    fsPath.status   = True
    fsPath.mesasge  = f"successfully changed path to {path}"
    return fsPath

def path_parts(options:Namespace, path:Path) -> tuple:
    if not path_isValid(options, path):
        return ()
    (root, db, collection) = path.parts
    return (db, collection)

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
def cd(ctx:click.Context, path:str) -> None:
    pudb.set_trace()
    options         = ctx.obj['options']
    target:Path     = fullPath_resolve(options, Path(path))
    path_isValid(options, target)
    cpath:Path      = smash.cwd(options)
    path_set(options, target)


