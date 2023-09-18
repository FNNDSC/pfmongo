import  click
from    pathlib import  Path
from    pfmisc  import  Colors as C

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

@click.command(help=f"""
               {GR}cat {CY}<file>{NC}  -- "Read" a <file>

This command shows the contents of <file>.

""")
@click.argument('path',
                required = False)
def cat(path:str) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)

