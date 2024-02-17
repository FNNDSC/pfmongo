import  click
from    argparse        import  Namespace
from    pfmongo         import  env, driver
from    pfmisc          import  Colors as C

from    pfmongo.commands.clop       import connect as collection
from    pfmongo.models              import responseModel
import  pudb
import  copy

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

from pfmongo.models.dataModel import messageType


def options_add(collection:str, options:Namespace) -> Namespace:
    localoptions:Namespace  = copy.deepcopy(options)
    localoptions.do         = 'deleteCollection'
    localoptions.argument   = collection
    return localoptions

def col_connectToTarget(options:Namespace) -> str:
    currentCol:str      = env.collectionName_get(options)
    if currentCol != options.argument:
        options.do      = 'connectCollection'
        collection.connectTo_asInt(options)
    return options.argument

def collectiondel_setup(options: Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    col_connectToTarget(options)
    options.do          = 'deleteCollection'
    return 0

def collectiondel_asInt(options:Namespace) -> int:
    fail:int            = 0
    if (fail := collectiondel_setup(options)):
        return fail
    return driver.run_intReturn(options)

def collectiondel_asModel(options:Namespace) -> responseModel.mongodbResponse:
    model:responseModel.mongodbResponse = responseModel.mongodbResponse()
    fail:int            = 0
    if (fail := collectiondel_setup(options)):
        model.message   = 'env failure'
        return model
    return driver.run_modelReturn(options)

@click.command(cls=env.CustomCommand, help=f"""
delete an entire {PL}COLLECTION{NC}

SYNOPSIS
{CY}deletecol {YL}<COLLECTION>{NC}

DESC
This subcommand removes an entire {YL}COLLECTION{NC} immediately.
Use with care! The system does not ask for confirmation!
""")
@click.argument('collection',
                required = True)
@click.pass_context
def deleteCol(ctx:click.Context, collection:str) -> int:
    # pudb.set_trace()
    # options:Namespace   = ctx.obj['options']
    return collectiondel_asInt(options_add(collection, ctx.obj['options']))
