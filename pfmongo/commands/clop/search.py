import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmongo         import  env
import  json
from    typing          import  Union
from    pfmisc          import  Colors as C
from    pfmongo.config  import  settings

from    pfmongo.commands.clop   import add

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType

# def collection_connect(collection:str, options:Namespace) -> int:
#     options.do          = 'connectCollection'
#     options.argument    = collection
#     return driver.run(options)

# def currentCollection_getName(options:Namespace) -> str:
#     currentCol:str      = env.collectionName_get(options)
#     if currentCol.endswith(settings.mongosettings.flattenSuffix):
#         currentCol = currentCol.rstrip(settings.mongosettings.flattenSuffix)
#         collection_connect(currentCol, options)
#     return currentCol

@click.command(help=f"""
{C.CYAN}search{NC} all documents in a collection for the union of tags in a
comma separated list.

The "hits" are returned referenced by the passed "field".
""")
@click.option('--target',
    type        = str,
    help        = \
    "A comma separated list. The logical AND of the search is returned",
    default     = '')
@click.option('--field',
    type        = str,
    help        = \
    "List the search hits referenced by this field",
    default     = '_id')
@click.pass_context
def search(ctx:click.Context, target:str, field:str) -> int:
    pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    thisCollection:str  = add.currentCollection_getName(options)
    options.do          = 'searchDocument'
    options.argument    = {
            "field":        field,
            "searchFor":    target.split(','),
            "collection":   thisCollection
    }
    hits:int              = driver.run(options)
    return hits
