from    argparse    import Namespace
import  click
from    pathlib     import Path
from    pfmisc      import Colors as C
from    pfmongo     import driver

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

def connectTo(database:str, options:Namespace) -> int:
    options.do          = 'connectDB'
    options.argument    = database
    return driver.run(options)

@click.command(help=f"""
               {GR}connect {CY}<database>{NC} -- connect to a mongo <database>

This command connects to a mongo database. A mongodb "server" can contain
several "databases".

""")
@click.argument('database',
                required = True)
@click.pass_context
def connect(ctx:click.Context, database:str) -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    return connectTo(database, options)
