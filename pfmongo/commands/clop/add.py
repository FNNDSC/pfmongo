import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
import  sys
from    pfmisc          import  Colors as C

NC  = C.NO_COLOUR


from pfmongo.models.dataModel import messageType

def env_failure(options:Namespace) -> int:
    envFailure:int    = driver.env_failCheck(options)
    if envFailure: return envFailure
    if not options.addDocument:
        return driver.complain(
            "The document to add was not specified", 1, messageType.ERROR
        )
    return 0

@click.command(help=f"""
{C.CYAN}add{NC} a document (read from the filesystem) to a collection

This subcommand accepts a document filename (assumed to contain JSON
formatted contents) and stores the contents in mongo.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI to the main group or in the system
environment.

""")
@click.option('--document',
              type  = str,
              help  = "A JSON formatted file to save to the collection in the database")
@click.option('--setid',
              type  = str,
              help  = "If specified, set the 'id' in the mongo collection to the passed string",
              default = '')
@click.pass_context
def add(ctx:click.Context, document:str):
    pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    if env_failure(options):
        return 100
    run:int = driver.run(options)
    print(f"Will add {document}")
    return run
