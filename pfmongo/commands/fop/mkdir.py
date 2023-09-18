import  click
from    pathlib import Path
from    pfmisc  import Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.command(help=f"""
               {GR}mkdir {CY}<path>{NC} -- make directory

The 'mkdir' command "creates a new directory" within a mongodb.
Depending on the apparent "level" of the <path>, this is either
a new <database> off the root `/` or a new collection off the
root.

""")
@click.argument('path',
                required = False)
def mkdir(path:str) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)


