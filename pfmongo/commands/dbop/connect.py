from    argparse        import Namespace
import  click
from    pfmisc          import Colors as C
from    pfmongo         import driver, env
from    pfmongo.models  import responseModel
import  pudb

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

def options_add(database:str, options:Namespace) -> Namespace:
    options.do          = 'connectDB'
    options.argument    = database
    return options

def connectTo_asInt(options:Namespace) -> int:
    return driver.run_intReturn(options)

def connectTo_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)

@click.command(cls = env.CustomCommand, help=f"""
{GR}DATABASE{NC} -- associate with a database context.

This command connects to a mongo database called {CY}DATABASE{NC}.
A mongodb "server" can contain several "databases". A {CY}DATABASE{NC}
is the lowest (or first) level of organization in monogodb.

""")
@click.argument('database',
                required = True)
@click.pass_context
def connect(ctx:click.Context, database:str) -> int:
    return connectTo_asInt(options_add(database, ctx.obj['options']))
