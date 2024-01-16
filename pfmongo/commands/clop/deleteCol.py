import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmongo         import  env
import  json
from    typing          import  Union
from    pfmisc          import  Colors as C
from    pfmongo.commands.clop         import  add

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType

def collection_delete(collection:str, options:Namespace) -> int:
    options.do          = 'deleteCollection'
    if env.env_failCheck(options):
        return 100
    collection_connectToTarget(collection, options)
    options.argument    = collection
    rem:int             = driver.run(options)
    return rem

def collection_connectToTarget(collection:str, options:Namespace) -> str:
    currentCol:str  = env.collectionName_get(options)
    if currentCol != collection:
        add.collection_connect(collection, options)
    return currentCol

@click.command(cls=env.CustomCommand, help=f"""
Deletes an entire <COLLECTION>

Use with care since there is no delete confirmation!

""")
@click.argument('collection',
                required = True)
@click.pass_context
def deleteCol(ctx:click.Context, collection:str) -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    return collection_delete(collection, options)
