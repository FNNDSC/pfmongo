import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmongo         import  env
import  json
from    typing          import  Union
from    pfmisc          import  Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType


@click.command(help=f"""
{C.CYAN}list{NC} all documents (read from the filesystem) in a collection

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""")
@click.option('--field',
    type        = str,
    help        = \
    "If specified, list only the named field",
    default     = '')
@click.pass_context
def list(ctx:click.Context, field:str) -> int:
    pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'list'
    options.argument    = field
    list:int            = driver.run(options)
    return list
