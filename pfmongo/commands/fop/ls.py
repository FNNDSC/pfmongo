import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel
from    pathlib         import  Path
import  ast
import  pudb
import  copy

from    pfmongo.commands.document   import showAll as doc
from    pfmongo.commands.database   import showAll as db
from    pfmongo.commands.collection import showAll as col
from    pfmongo.commands.fop.pwd    import pwd_level
import  pwd

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

def options_add(path:str, attribs:str, long:bool, options:Namespace) -> Namespace:
    localoptions            = copy.deepcopy(options)
    localoptions.do         = 'ls'
    localoptions.argument   = {
            "path":     path,
            "attribs":  attribs,
            "long":     long
    }
    return localoptions

def resp_process(resp:responseModel.mongodbResponse) -> None:
    file:list   = ast.literal_eval(resp.message)
    for f in file:
        print(f)

def ls_db(options:Namespace) -> responseModel.mongodbResponse :
    resp    = db.showAll_asModel(
                driver.settmp(
                    db.options_add(options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def ls_collection(options:Namespace) -> responseModel.mongodbResponse :
    resp    = col.showAll_asModel(
                driver.settmp(
                    col.options_add(options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def ls_doc(options:Namespace) -> responseModel.mongodbResponse:
    resp    = doc.showAll_asModel(
                driver.settmp(
                    doc.options_add('_id', options),
                    [{'beQuiet': True}]
                )
            )
    return resp

def ls_do(options:Namespace) -> tuple[int, responseModel.mongodbResponse]:
    resp:responseModel.mongodbResponse  = responseModel.mongodbResponse()
    match pwd_level(options):
        case "root":        resp    = ls_db(options)
        case "database":    resp    = ls_collection(options)
        case "collection":  resp    = ls_doc(options)
        case "_":           resp    = ls_db(options)
    if not options.beQuiet:
        resp_process(resp)
    ret:int     = 0
    if not resp.message:
        ret     = 1
    return ret, resp

def ls_asInt(options:Namespace) -> int:
    ret, resp   = ls_do(options)
    return ret

def ls_asModel(options:Namespace) -> responseModel.mongodbResponse:
    ret, resp   = ls_do(options)
    return resp

@click.command(cls = env.CustomCommand, help=f"""
list files

SYNOPSIS
{CY}ls {YL}[--long] ]--human] <path>{NC}

ARGS
This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.

The {YL}--long{NC} flag triggers a detailed listing, showing analogues to
the document or "file" {CY}owner{NC}, {CY}size{NC}, and creation {CY}date{NC}.
This assumes that the document entry has these fields encoded, which is only
true for files uploaded using {YL}pfmongo{NC}.


""")
@click.argument('path',
                required = False)
@click.option('--attribs',  required = False,
              help      = 'A comma separated list of file attributes to return/print')
@click.option('--long',
              is_flag   = True,
              help      = 'If set, use a long listing format')
@click.pass_context
def ls(ctx:click.Context, path:str, attribs:str, long:bool) -> int:
    # pudb.set_trace()
    return ls_asInt(options_add(path, attribs, long, ctx.obj['options']))
