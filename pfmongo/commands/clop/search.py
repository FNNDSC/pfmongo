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
{C.CYAN}search{NC} all documents in a collection for the union of tags in a
comma separated list.

The "hits" are returned referenced by the passed "field".
""")
@click.option('--for',
    type        = str,
    help        = \
    "A comma separated list. The logical AND of the search is returned",
    default     = '_id')
@click.option('--field',
    type        = str,
    help        = \
    "List the search hits referenced by this field",
    default     = '_id')
@click.pass_context
def list(ctx:click.Context, searchFor:str, field:str) -> int:
    pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'searchDocument'
    options.argument    = {
            "field":        field,
            "searchFor":    searchFor.split(',')
    }
    hits:int              = driver.run(options)
    return hits
