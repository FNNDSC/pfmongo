import  click
import  pudb
from    pfmongo         import  driver
from    argparse        import  Namespace
from    pfmongo         import  env
import  json
from    typing          import  Union
from    pfmisc          import  Colors as C
from    pfmongo.commands.dbop   import  connect as db

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from pfmongo.models.dataModel import messageType

def DB_connectToTarget(DB:str, options:Namespace) -> str:
    currentDB:str  = env.DBname_get(options)
    if currentDB!= DB:
        db.connectTo(DB, options)
    return currentDB

@click.command(help=f"""
{GR}deletedb {C.CYAN}<database>{NC} delete an entire database

This subcommand removes an entire <database>.

""")
@click.argument('db',
                required = True)
@click.pass_context
def deleteDB(ctx:click.Context, db:str) -> int:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    if env.env_failCheck(options):
        return 100
    DB_connectToTarget(db, options)
    options.do          = 'deleteDB'
    options.argument    = db
    rem:int             = driver.run(options)
    return rem
