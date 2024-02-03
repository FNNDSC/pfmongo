import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel
import  copy
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW

def options_add(field:str, options:Namespace) -> Namespace:
    localoptions:Namespace  = copy.deepcopy(options)
    localoptions.do         = 'listDocument'
    localoptions.argument   = field
    return localoptions

def showAll_asInt(options:Namespace) -> int:
    return driver.run_intReturn(options)

def showAll_asModel(options:Namespace) -> responseModel.mongodbResponse:
    return driver.run_modelReturn(options)

@click.command(cls = env.CustomCommand, help=f"""
list {PL}documents{NC} in a collection.

SYNPOSIS
{CY}showall {YL}[--field <field>]{NC}

DESC
List all the documents in a collection, showing the contents of the
document's {YL}<field>{NC} key (by default this is '{YL}_id{NC}').

""")
@click.option('--field',
    type        = str,
    help        = \
    "List the value of the named field",
    default     = '_id')
@click.pass_context
def showAll(ctx:click.Context, field:str) -> int:
    # pudb.set_trace()
    return showAll_asInt(options_add(field, ctx.obj['options']))
