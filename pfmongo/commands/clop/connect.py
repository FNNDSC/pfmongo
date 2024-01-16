from    argparse    import Namespace
import  click
from    pathlib     import Path
from    pfmisc      import Colors as C
from    pfmongo     import driver, env

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

@click.command(cls=env.CustomCommand, help=f"""
Connect to a mongo <COLLECTION>

SYNOPSIS
{GR}connect {CY}<collection>{NC} -- connect to a mongo <collection>

DESC
This command connects to a mongo collection within a mongo database.
A mongodb "server" can contain several "databases", each of which
contains several "collections".

""")
@click.argument('collection',
                required = True)
@click.pass_context
def connect(ctx:click.Context, collection:str) -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'connectCollection'
    options.argument    = collection
    return driver.run(options)
