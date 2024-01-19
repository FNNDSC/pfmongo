import  click
from    argparse        import  Namespace
from    pfmongo         import  env, driver
from    pfmisc          import  Colors as C

from    pfmongo.commands.dbop   import  connect as db
from    pfmongo.models          import  responseModel
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType


def options_add(database:str, options:Namespace) -> Namespace:
    options.do          = 'deleteDB'
    options.argument    = database
    return options

def DB_connectToTarget(options:Namespace) -> str:
    currentDB:str  = env.DBname_get(options)
    if currentDB != options.argument:
        options.do      = 'connectDB'
        db.connectTo_asInt(options)
    return options.argument

def DBdel_setup(options: Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    DB_connectToTarget(options)
    options.do          = 'deleteDB'
    return 0

def DBdel_asInt(options:Namespace) -> int:
    fail:int            = 0
    if (fail := DBdel_setup(options)):
        return fail
    return driver.run_intReturn(options)

def DBdel_asModel(options:Namespace) -> responseModel.mongodbResponse:
    model:responseModel.mongodbResponse = responseModel.mongodbResponse()
    fail:int            = 0
    if (fail := DBdel_setup(options)):
        model.message   = 'env failure'
        return model
    return driver.run_modelReturn(options)

@click.command(cls = env.CustomCommand, help=f"""
{GR}DATABASE{NC} -- delete an entire database

This subcommand removes an entire {GR}DATABASE{NC} immediately.
Use with care! No confirmation is asked by the system!

""")
@click.argument('database',
                required = True)
@click.pass_context
def deleteDB(ctx:click.Context, database:str) -> int:
    # pudb.set_trace()
    return DBdel_asInt(options_add(database, ctx.obj['options']))
    # options:Namespace   = ctx.obj['options']
    # if env.env_failCheck(options):
    #     return 100
    # DB_connectToTarget(db, options)
    # options.do          = 'deleteDB'
    # options.argument    = db
    # rem:int             = driver.run(options)
    # return rem
