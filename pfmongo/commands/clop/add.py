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

def env_OK(options:Namespace, d_doc:dict) -> bool|dict:
    envFailure:int    = env.env_failCheck(options)
    if envFailure: return False
    if not d_doc['status']:
        return not bool(env.complain(
            d_doc['data'], 1, messageType.ERROR
        ))
    if 'data' in d_doc:
        return d_doc['data']
    else:
        return False

def jsonFile_intoDictRead(filename:str) -> dict[bool,dict]:
    d_json:dict     = {
        'status':   False,
        'filename': filename,
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
    help  = \
    "The name of a JSON formatted file to save to the collection in the database")
@click.option('--id',
    type  = str,
    help  = \
    "If specified, set the 'id' in the mongo collection to the passed string",
    default = '')
@click.pass_context
def add(ctx:click.Context, document:str, id:str="") -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'addDocument'
    d_dataOK:dict|bool  = env_OK(options, jsonFile_intoDictRead(document))
    d_data:dict         = {}
    if not d_dataOK:
        return 100
    if isinstance(d_dataOK, dict):
        d_data          = d_dataOK
    if id:
        d_data['_id']   = id
    options.argument    = d_data
    save:int            = driver.run(options)
    return save
