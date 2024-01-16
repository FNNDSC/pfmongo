import  click
import  pudb
from    pfmongo                 import  driver
from    argparse                import  Namespace
from    pfmongo                 import  env
from    pfmisc                  import  Colors as C
from    pfmongo.commands.clop   import add
from    pfmongo.config          import settings


NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

def delete_do(id:str, options:Namespace) -> int:
    thisCollection:str      = add.currentCollection_getName(options)
    delFail:int             = document_delete(id, options)
    if settings.appsettings.donotFlatten or delFail:
        return delFail
    options.collectionName  = add.shadowCollection_getName(options)
    delFail:int             = document_delete(id, options)
    options.collectionName  = thisCollection
    add.collection_connect(thisCollection, options)
    return delFail

def document_delete(id:str, options:Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    options.do          = 'deleteDocument'
    options.argument    = id
    rem:int             = driver.run(options)
    return rem

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
    "Delete the document with the passed 'id'",
    default = '')
@click.pass_context
def delete(ctx:click.Context, id:str="") -> int:
    # pudb.set_trace()
    return delete_do(id, ctx.obj['options'])
