import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
import  env
import  json
from    pfmisc          import  Colors as C

NC  = C.NO_COLOUR


from pfmongo.models.dataModel import messageType

def env_failure(options:Namespace) -> int:
    envFailure:int    = env.env_failCheck(options)
    if envFailure: return envFailure
    if not options.addDocument:
        return env.complain(
            "The document to add was not specified", 1, messageType.ERROR
        )
    return 0


def jsonFile_intoDictRead(filename:str) -> dict[bool,dict]:
    d_json:dict     = {
        'status':   False,
        'data':     {}
    }
    try:
        f = open(filename)
        d_json['data']      = json.load(f)
        d_json['status']    = True
    except Exception as e:
        d_json['data']      = str(e)
    return d_json


@click.command(help=f"""
{C.CYAN}add{NC} a document (read from the filesystem) to a collection

This subcommand accepts a document filename (assumed to contain JSON
formatted contents) and stores the contents in mongo.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

""")
@click.option('--document',
    type  = str,
    help  = "A JSON formatted file to save to the collection in the database")
@click.option('--setid',
    type  = str,
    help  = \
    "If specified, set the 'id' in the mongo collection to the passed string",
    default = '')
@click.pass_context
def add(ctx:click.Context, document:str, setid:str=""):
    pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'addDocument'
    options.argument    = f'{document},{setid}'
    if env_failure(options):
        return 100
    add:int = driver.run(options)
    print(f"Will add {document}")
    return add
