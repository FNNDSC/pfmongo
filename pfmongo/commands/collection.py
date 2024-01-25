from    pfmisc      import  Colors  as C
from    pfmongo.commands.clop   import showAll, connect, deleteCol
from    pfmongo     import env
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.group(cls=env.CustomGroup,  help = f"""
    commands suitable for collection focus: {GR}show, connect, deletecol{NC}

    This command group provides mongo {CY}"collection"{NC} level commands,
    primarily used to {CY}connect {NC}to a collection, {CY}showall{NC} collections,
    and also {CY}deletecol{NC} collections.

    Use the {CY}deletecol{NC} subcommand with care, since it will delete
    without asking for confirmation.
"""
)
def collection():
    pass

collection.add_command(showAll.showAll)
collection.add_command(connect.connect)
collection.add_command(deleteCol.deleteCol)
