from    argparse        import Namespace
import  click
from    pfmisc          import Colors as C
from    pfmongo         import driver, env
from    pfmongo.models  import responseModel
from    pfmongo.config  import settings
from    typing          import Tuple
import  copy
NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


def options_add(collection:str, options:Namespace) -> Namespace:
    options.do          = 'connectCollection'
    options.argument    = collection
    return options

def is_shadowCollection(collection:str) -> Tuple[str, bool]:
    isShadow:bool = True if collection.endswith(settings.mongosettings.flattenSuffix) \
                    else False
    return collection, isShadow

def baseCollection_getAndConnect(options:Namespace) -> Namespace:
    localoptions        = copy.deepcopy(options)
    localoptions.collectionName = env.collectionName_get(localoptions)
    currentCol:str      = env.collectionName_get(options)
    if currentCol.endswith(settings.mongosettings.flattenSuffix):
        currentCol      = currentCol.rstrip(settings.mongosettings.flattenSuffix)
        localoptions    = collection_connect(currentCol, options)
    return localoptions

def shadowCollection_getAndConnect(options:Namespace) -> Namespace:
    localoptions        = copy.deepcopy(options)
    localoptions.collectionName = env.collectionName_get(localoptions)
    shadowCol:str       = ""
    if not (currentCol := is_shadowCollection(env.collectionName_get(options)))[1]:
        shadowSuffix:str    = settings.mongosettings.flattenSuffix
        shadowCol:str       = currentCol[0] + shadowSuffix
        localoptions        = collection_connect(shadowCol, options)
    return localoptions

def collection_connect(collection:str, options:Namespace) -> Namespace:
    """ Returns a copy of the options with the following
        state changes:

            1. 'runRet' contains the int result of doing a connection
                        to the <collection>. This run is also performed
                        on its own options copy.
            2. 'collectionName' in the original copy is updated to the
                                <collection>.

        Note the original options passed into this method is *unchanged*!
    """
    return driver.settmp(options,
            [{'runRet':
                driver.run_intReturn(
                    driver.settmp(options,
                        [{'do': 'connectCollection'}, {'argument': collection}])
                    )
            },
            {'collectionName': collection}]
    )

def connectTo_asInt(options:Namespace) -> int:
    return driver.run_intReturn(options)

def connectTo_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)

@click.command(cls=env.CustomCommand, help=f"""
associate context with {PL}COLLECTION{NC}

SYNOPSIS
{CY}connect {YL}<COLLECTION>{NC}

DESC
This command connects to a mongo collection called {YL}COLLECTION{NC}
within a mongo database.

A mongodb "server" can contain several "databases", each of which
contains several "collections".

A {YL}COLLECTION{NC} is the second level of organization in a monogdb.

""")
@click.argument('collection',
                required = True)
@click.pass_context
def connect(ctx:click.Context, collection:str) -> int:
    # pudb.set_trace()
    return connectTo_asInt(options_add(collection, ctx.obj['options']))
