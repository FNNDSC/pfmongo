import  click
from    argparse    import  Namespace
import  pudb
from    pfmisc      import  Colors as C
from    pfmongo     import  env, pfmongo, driver
from    pfmongo.models  import responseModel

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

def stateResponse_eval(mongodb:pfmongo.Pfmongo) -> pfmongo.Pfmongo:
    mongodb.responseData    = mongo_responseEmbed(
                                state_get(mongodb.args)
                              )
    mongodb.exitCode        = 0
    return mongodb

def state_get(options:Namespace) -> responseModel.stateResponse:
    state:responseModel.stateResponse   = responseModel.stateResponse()
    state.database          = env.DBname_get(options)
    state.collection        = env.collectionName_get(options)
    return state

def mongo_responseEmbed(state:responseModel.stateResponse) \
    -> responseModel.mongodbResponse:
    return pfmongo.responseData_build(
        {
            'status':   True,
            'connect':  state
        }, "Internal state response"
    )

@click.command(help=f"""
               {GR}showall{NC} -- show internal state values

This command shows internal program state. It accepts no arguments.

""")
@click.pass_context
def showAll(ctx:click.Context) -> int:
    #pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'showAllState'
    showall:int         = driver.run(options, stateResponse_eval)
    return showall
