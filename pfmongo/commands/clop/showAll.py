import  click
from    argparse    import  Namespace
from    pathlib     import  Path
from    pfmisc      import  Colors as C
from    pfmongo     import  driver

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

@click.command(help=f"""
               {GR}showall{NC} -- show all collections

This command shows all the collections available in a given database
in a mongodb server. It accepts no arguments.

""")
@click.pass_context
def showAll(ctx:click.Context) -> None:
    # pudb.set_trace()
    options:Namespace   = ctx.obj['options']
    options.do          = 'showAllCollections'
    showall:int         = driver.run(options)
