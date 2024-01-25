from    pfmongo     import  env
from    pfmisc      import  Colors  as C
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

from    pfmongo.commands.stateop    import showAll

@click.group(cls = env.CustomGroup, help=f"""
internal state commands

This command group provides commands operating on internal state.
For the most part, this is simply a {CY}showall{NC} that shows the internal
state (notably the current database and collection of focus).

More information can be returned by calling {GR}pfmongo{NC} with a
{YL}--detailedOutput{NC} flag.

""")
def state():
    pass

state.add_command(showAll.showAll)

