import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmisc          import  Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

def collection_list(field:str, options:Namespace) -> int:
    options.do          = 'listDocument'
    options.argument    = field
    ls:int              = driver.run(options)
    return ls

@click.command(help=f"""
{C.CYAN}list{NC} all documents (read from the filesystem) in a collection

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""")
@click.option('--field',
    type        = str,
    help        = \
    "List the value of the named field",
    default     = '_id')
@click.pass_context
def list(ctx:click.Context, field:str) -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    return collection_list(field, options)
