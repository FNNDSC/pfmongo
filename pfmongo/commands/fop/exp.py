import  click
from    pathlib import Path
from    pfmisc  import Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.command(help=f"""
{GR}exp {CY}<pathIN> <pathEX>{NC} -- export <pathIN> to <pathEX>

The {GR}exp{NC} command "exports" a document {CY}pathIN{NC} to the real filesystem
at {GR}pathEX{NC}.


""")
@click.argument('pathIN',
                required = True)
@click.argument('pathEX',
                required = True)
def exp(path:str) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)


