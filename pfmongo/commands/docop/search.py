import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmisc          import  Colors as C

from    pfmongo.commands.clop   import add

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

def document_search(target:str, field:str, options:Namespace) ->int:
    thisCollection:str  = add.currentCollection_getName(options)
    flatCollection:str  = add.shadowCollection_getName(options)
    options.do          = 'searchDocument'
    options.argument    = {
            "field":        field,
            "searchFor":    target.split(','),
            "collection":   thisCollection
    }
    hits:int              = driver.run(options)
    add.currentCollection_getName(options)
    return hits

@click.command(help=f"""
{C.CYAN}search{NC} all documents in a collection for the union of tags in a
comma separated list.

The "hits" are returned referenced by the passed "field".
""")
@click.option('--target',
    type        = str,
    help        = \
    "A comma separated list. The logical OR of the search is returned",
    default     = '')
@click.option('--field',
    type        = str,
    help        = \
    "List the search hits referenced by this field",
    default     = '_id')
@click.pass_context
def search(ctx:click.Context, target:str, field:str) -> int:
    # pudb.set_trace()
    return document_search(target, field, ctx.obj['options'])
