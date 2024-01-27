from    argparse        import Namespace
import  click
from    pfmisc          import Colors as C
from    pfmongo         import driver, env
from    pfmongo.models  import responseModel
from    copy            import deepcopy
import  pudb

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
YL = C.YELLOW
PL = C.PURPLE

def options_add(database:str, options:Namespace) -> Namespace:
    localoptions:Namespace   = deepcopy(options)
    localoptions.do          = 'connectDB'
    localoptions.argument    = database
    return localoptions

def connectTo_asInt(options:Namespace) -> int:
    return driver.run_intReturn(options)

def connectTo_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)

@click.command(cls = env.CustomCommand, help=f"""
associate a context with {PL}DATABASE{NC}

SYNOPSIS
{CY}connect {YL}<DATABASE>{NC}

DESC
This command connects to a mongo database called {YL}DATABASE{NC}.
A mongodb "server" can contain several "databases". A {YL}DATABASE{NC}
is the lowest (or first) level of organization in monogodb.

In order to do any operations on data, you first MUST connect to
a {PL}DATABASE{NC}.
""")
@click.argument('database',
                required = True)
@click.pass_context
def connect(ctx:click.Context, database:str) -> int:
    return connectTo_asInt(options_add(database, ctx.obj['options']))
