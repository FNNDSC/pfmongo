import  click
import  click
import  pudb
from    pfmongo         import driver, env
from    argparse        import Namespace
from    pfmongo.models  import responseModel
from    pfmisc          import Colors as C
import  copy
from    pathlib         import Path
from    pfmongo.models  import fsModel, responseModel

import  pfmongo.commands.smash      as smash
import  pfmongo.commands.fop.cd     as cd
import  pfmongo.commands.docop.get  as get
from    pfmongo.commands.fop.pwd    import pwd_level
from    pfmongo.commands.document   import delete    as doc
from    pfmongo.commands.database   import deleteDB  as db
from    pfmongo.commands.collection import deleteCol as col



NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

def options_add(file:str, options:Namespace) -> Namespace:
    localoptions:Namespace  = copy.deepcopy(options)
    localoptions.do         = 'rm'
    localoptions.file       = Path(file)
    localoptions.beQuiet    = True
    return localoptions

# def path_process(options:Namespace) -> fsModel.cdResponse:
#     dir:Path    = options.file.parent

#     return cd.changeDirectory(cd.options_add(str(dir), options))

def rm_db(options:Namespace) -> responseModel.mongodbResponse :
    resp    = db.DBdel_asModel(
                driver.settmp(
                    db.options_add(str(options.file), options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def rm_collection(options:Namespace) -> responseModel.mongodbResponse :
    resp    = col.collectiondel_asModel(
                driver.settmp(
                    col.options_add(str(options.file), options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def rm_doc(options:Namespace) -> responseModel.mongodbResponse:
    resp    = doc.deleteDo_asModel(
                driver.settmp(
                    doc.options_add('_id', options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def cd_toParent(options:Namespace) -> fsModel.cdResponse:
    return  cd.changeDirectory(
                cd.options_add(options.file.parent, options)
            )

def rm_setName(options:Namespace) -> Namespace:
    cdResp:fsModel.cdResponse           = fsModel.cdResponse()
    cdResp  = cd_toParent(options)
    if cdResp.status:
        options.file = options.file.name
    return options

def rm_do(options:Namespace) -> tuple[int, responseModel.mongodbResponse]:
    cwd:Path                    = smash.cwd(options)
    resp:responseModel.mongodbResponse  = responseModel.mongodbResponse()
    cdResp:fsModel.cdResponse           = fsModel.cdResponse()
    if not (cdResp:=cd_toParent(options)).status:
        resp.message    = cdResp.message
        return 1, resp

    match pwd_level(options):
        case "root":        resp = rm_db(options)
        case "database":    resp = rm_collection(options)
        case "collection":  resp = rm_doc(options)
        case "_":           resp.message = "invalid directory level"
    if not options.beQuiet:
        print(resp.message)
    ret:int     = 0
    if not resp.message:
        ret     = 1
    cd.changeDirectory(cd.options_add(str(cwd), options))
    return ret, resp

def rm_asInt(options:Namespace) -> int:
    ret, resp   = rm_do(options)
    return ret

def rm_asModel(options:Namespace) -> responseModel.mongodbResponse:
    ret, resp   = rm_do(options)
    return resp

@click.command(cls = env.CustomCommand, help=f"""
delete {YL}path{NC}

SYNOPSIS
{CY}rm {YL}<path>{NC}

DESC
Delete a {YL}path{NC}. Note that the {YL}<path>{NC} can consist of a
{YL}<path>{NC} prefix specifier denoting the {YL}database{NC} and {YL}collection{NC}
to delete.

""")
@click.pass_context
@click.argument('path',
                required = False)
def rm(ctx:click.Context, path:str) -> int:
    pudb.set_trace()
    return rm_do(options_add(path, ctx.obj['options']))
