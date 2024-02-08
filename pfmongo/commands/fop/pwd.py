import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel, fsModel
from    pathlib         import  Path
import  copy
import  ast
import  pudb

from    pfmongo.commands.document   import showAll as doc
from    pfmongo.commands.state      import showAll as state
import  pfmongo.commands.smash      as smash

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

def options_add(options:Namespace) -> Namespace:
    localoptions:Namespace  = copy.deepcopy(options)
    localoptions.beQuiet    = True
    return localoptions

def pwd_level(options:Namespace) -> str:
    match len(smash.cwd(options).parts):
        case 1: return "root"
        case 2: return "database"
        case 3: return "collection"
        case _: return "unknown"

def dir_level(dir:fsModel.cdResponse) -> str:
    match len(dir.path.parts):
        case 1: return "root"
        case 2: return "database"
        case 3: return "collection"
        case _: return "unknown"

def pwd_do(options:Namespace) -> fsModel.cdResponse:
    pathResp            = fsModel.cdResponse()
    resp:responseModel.mongodbResponse   = state.showAll_asModel(options)
    if resp.message     == '/':
        pathResp.path   = Path(resp.message)
    else:
        pathResp.path   = Path('/') /  Path(resp.message)
    pathResp.status     = True
    return pathResp

def pwd_asInt(options):
    pathResp:fsModel.cdResponse = pwd_do(options)
    print(pathResp.path)
    return pathResp.code

@click.command(cls = env.CustomCommand, help=f"""
print working {YL}directory{NC}

SYNOPSIS
{CY}pwd{NC}

DESC
This command simply returns the current "working directory".

""")
@click.pass_context
def pwd(ctx:click.Context) -> int:
    # pudb.set_trace()
    return pwd_asInt(options_add(ctx.obj['options']))
