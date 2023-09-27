import  click
from    argparse    import  Namespace
from    pathlib     import  Path
from    pfmisc      import  Colors as C
from    pfmongo     import  driver

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

@click.command(help=f"""
               {GR}showall{NC} -- show all databases

This command shows all the databases available in a given mongodb
server. It accepts no arguments.

""")
@click.pass_context
def showAll(ctx:click.Context) -> None:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'showAllDB'
    showall:int         = driver.run(options)
