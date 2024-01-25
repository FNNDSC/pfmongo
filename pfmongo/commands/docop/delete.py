import  click
import  pudb
from    pfmongo                 import  driver
from    argparse                import  Namespace
from    pfmongo                 import  env
from    pfmisc                  import  Colors as C
from    pfmongo.config          import  settings
from    pfmongo.commands.clop   import  connect
from    pfmongo.models          import  responseModel
from    typing                  import  cast

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

def options_add(id:str, options:Namespace) -> Namespace:
    options.do          = 'deleteDocument'
    options.argument    = id
    return options

def env_check(options:Namespace) -> int:
    if env.env_failCheck(options):
        return 100
    return 0

def run_check(
        failData:int, message:str = "early failure", returnType:str = "int"
) -> tuple[int, int|responseModel.mongodbResponse]:
    reti:int        = failData
    retm:responseModel.mongodbResponse  = responseModel.mongodbResponse()
    if reti:
        retm.message    = f' {message} (code {reti}) occurred in document delete'
    match returnType:
        case 'int':     return reti, reti
        case 'model':   return reti, retm
        case _:         return reti, reti

def delete_do(options:Namespace, returnType:str="int") -> int|responseModel.mongodbResponse:
    failEnv:int           = 0
    if (failEnv := env_check(options)):
        return run_check(failEnv, 'failure in document del setup', returnType)[1]

    if (failDel := run_check(
                            driver.run_intReturn(connect.baseCollection_getAndConnect(options)),
                            'failure in document base collection delete',
                            returnType)
                    )[0]:
        return failDel[1]

    if not settings.appsettings.donotFlatten:
        failDel = run_check(
                            driver.run_intReturn(connect.shadowCollection_getAndConnect(options)),
                            'failure in document shadow collection delete',
                            returnType)
    return failDel[1]

def deleteDo_asInt(options:Namespace) -> int:
    return cast(int, delete_do(options, 'int'))

def deleteDo_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return cast(responseModel.mongodbResponse, delete_do(options, 'model'))

@click.command(cls = env.CustomCommand, help=f"""
remove a {YL}document{NC} from a collection

SYNOPSIS
{CY}delete {GR}--id {YL}<id>{NC}

DESC
This subcommand removes a {YL}document{NC} identified by {YL}<id>{NC} from a collection.

The "location" is defined by the core parameters, 'useDB' and 'useCollection'
which are typically defined in the CLI, in the system environment, or in the
session state.

Use with care. No confirmation is asked!

""")
@click.option('--id',
    type  = str,
    help  = \
    "Delete the document with the passed 'id'",
    default = '')
@click.pass_context
def delete(ctx:click.Context, id:str="") -> int:
    # pudb.set_trace()
    return deleteDo_asInt(options_add(id, ctx.obj['options']))

