import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmongo         import  env
import  json
from    typing          import  Union
from    pfmisc          import  Colors as C
from    pfmongo.config  import  settings

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType

def flatten_dict(data:dict, parent_key:str='', sep:str='/') -> dict:
    flattened:dict = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flattened.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                list_key = f"{new_key}{sep}{i}"
                if isinstance(item, (dict, list)):
                    flattened.update(flatten_dict({str(i): item}, parent_key=list_key, sep=sep))
                else:
                    flattened[list_key] = item
        else:
            flattened[new_key] = v
    return flattened

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

def upload(d_data:dict, options:Namespace, id:str="") -> int:
    if id:
        d_data['_id']   = id
    d_data['_size']     = driver.get_size(d_data)
    options.do          = 'addDocument'
    options.argument    = d_data
    do:int              = driver.run(options)
    return do

def currentCollection_getName(options:Namespace) -> str:
    currentCol:str      = env.collectionName_get(options)
    if currentCol.endswith(settings.mongosettings.flattenSuffix):
        currentCol = currentCol.rstrip(settings.mongosettings.flattenSuffix)
        collection_connect(currentCol, options)
    return currentCol

def shadowCollection_getName(options:Namespace) -> str:
    sourceCol:str       = env.collectionName_get(options)
    shadowSuffix:str    = settings.mongosettings.flattenSuffix
    shadowCol:str       = sourceCol + shadowSuffix
    collection_connect(shadowCol, options)
    return shadowCol

def collection_connect(collection:str, options:Namespace) -> int:
    options.do          = 'connectCollection'
    options.argument    = collection
    return driver.run(options)

def add_do(document:dict, id:str, options:Namespace) -> int:
    thisCollection:str      = currentCollection_getName(options)
    # pudb.set_trace()
    saveFail:int            = upload(document, options, id)
    if settings.appsettings.donotFlatten or saveFail:
        return saveFail
    # pudb.set_trace()
    options.collectionName  = shadowCollection_getName(options)
    saveFail                = upload(flatten_dict(document), options, id)
    options.collectionName  = thisCollection
    connect:int             = collection_connect(thisCollection, options)
    return saveFail

def document_add(documentFile:str, id:str, options:Namespace) -> int:
    d_dataOK:dict|bool  = env_OK(options, jsonFile_intoDictRead(documentFile))
    d_data:dict         = {}
    if not d_dataOK:
        return 100
    if isinstance(d_dataOK, dict):
        d_data          = d_dataOK
    saveFail:int        = add_do(d_data, id, options)
    return saveFail

@click.command(help=f"""
{C.CYAN}add{NC} a document (read from the filesystem) to a collection

This subcommand accepts a document filename (assumed to contain JSON
formatted contents) and stores the contents in mongo.

A "shadow" document with a flat dataspace is also added to a "shadow"
collection. This "shadow" document facilitates searching and is kept
"in sync" with the orginal.

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
    return document_add(document, id, ctx.obj['options'])
