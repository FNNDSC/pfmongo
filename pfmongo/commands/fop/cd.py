from    argparse    import Namespace
from    pathlib     import Path
from    pfmisc      import Colors as C
from    pfmongo.commands    import fs
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

def cwd(options:Namespace):
   pass

@click.command(help=f"""
               {GR}cd {CY}[<path>]{NC} -- change directory

The 'cd' command "changes directory" within a mongodb between a
<database> level at the root `/` and a collection within a
<database>

""")
@click.argument('path',
                required = False)
@click.pass_context
def cd(ctx:click.Context, path:str) -> None:
    pudb.set_trace()
    options         = ctx.obj['options']
    target:Path     = Path('')
    if path:
        target = Path(path)
    sessionRoot:Path   = fs.root(options)


