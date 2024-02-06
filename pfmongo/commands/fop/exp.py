import  click
from    pathlib import Path
from    pfmisc  import Colors as C

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

@click.command(help=f"""
export a {YL}document{NC} to a {CY}file{NC}

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


