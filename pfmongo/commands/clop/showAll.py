import  click
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo         import  driver, env
from    pfmongo.models  import responseModel
import  copy

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
YL = C.YELLOW
PL = C.PURPLE

def options_add(options:Namespace) -> Namespace:
    localoptions:Namespace  = copy.deepcopy(options)
    localoptions.do         = 'showAllCollections'
    return localoptions

def showAll_asInt(options:Namespace) -> int:
    return driver.run_intReturn(options)

def showAll_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)

@click.command(cls=env.CustomCommand, help=f"""
list {PL}COLLECTIONS{NC} containing data in a {PL}DATABASE{NC}.

SYNOPSIS
{CY}showall{NC}

DESC
This command shows all the collections available in a given database
in a mongodb server. It accepts no arguments.

""")
@click.pass_context
def showAll(ctx:click.Context) -> int:
    # pudb.set_trace()
    return showAll_asInt(options_add(ctx.obj['options']))
