import  click
from    pfmongo         import  driver, env
from    argparse        import  Namespace
from    pfmisc          import  Colors as C
from    pfmongo.models  import  responseModel
from    pathlib         import  Path
import  ast
import  pudb

from    pfmongo.commands.document import showAll as doc

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
PL  = C.PURPLE
YL  = C.YELLOW


def resp_process(resp:responseModel.mongodbResponse) -> None:
    file:list   = ast.literal_eval(resp.message)
    for f in file:
        print(f)

@click.command(cls = env.CustomCommand, help=f"""
{CY}<args>{NC} -- list files

SYNOPSIS
{CY}ls {YL}[--long] <path>{NC}

ARGS
This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.

The {YL}-l{NC} flag triggers a detailed listing.

""")
@click.argument('path',
                required = False)
@click.option('--attribs',  required = False,
              help      = 'A comma separated list of file attributes to return/print')
@click.option('--long',
              is_flag   = True,
              help      = 'If set, use a long listing format')
@click.pass_context
def ls(ctx:click.Context, path:str, attribs:str, long:bool) -> None:
    pudb.set_trace()
    resp:responseModel.mongodbResponse  = responseModel.mongodbResponse()
    resp = doc.showAll_asModel(
            driver.settmp(
                doc.options_add('_id', ctx.obj['options']),
                                [{'beQuiet': True}]))
    resp_process(resp)
    target:Path     = Path('')
    if path:
        target = Path(path)

