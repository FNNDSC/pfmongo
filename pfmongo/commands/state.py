from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
from    pfmisc      import  Colors  as C
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

from    pfmongo.commands.stateop    import showAll

#try:
#    from    dbop    import  connect, showAll
#except:
#    from    .dbop   import  connect, showAll


@click.group(help=f"""
             {GR}state {CY}<cmd>{NC} -- internal state commands

This command group provides commands operating on internal state.

""")
def state():
    pass

state.add_command(showAll.showAll)

