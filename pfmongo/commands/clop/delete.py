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
{C.CYAN}delete{NC} a document from a collection

This subcommand removes a document with passed 'id' from a collection.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""")
@click.option('--id',
    type  = str,
    help  = \
    "If specified, delete the document with the passed 'id'",
    default = '')
@click.pass_context
def delete(ctx:click.Context, id:str="") -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'deleteDocument'
    if env.env_failCheck(options):
        return 100
    options.argument    = id
    rem:int             = driver.run(options)
    return rem
