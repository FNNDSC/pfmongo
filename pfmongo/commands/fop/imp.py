import  click
from    pathlib import Path
from    pfmisc  import Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.command(help=f"""
{GR}imp {CY}<pathEX> <pathIN>{NC} -- import a file as a document

The {GR}imp{NC} command "imports" a file {CY}pathEX{NC} on the real filesystem
to the collection document in {CY}pathIN{NC}.


""")
@click.argument('pathEX',
                required = True)
@click.argument('pathIN',
                required = True)
def imp(path:str) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)


