from pfmisc import Colors as C
import click
import pudb
from pfmongo import env
from pfmongo.commands.dbop import connect, showAll, deleteDB


NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN


@click.group(
    cls=env.CustomGroup,
    help=f"""
commands suitable for database focus: {GR}show, connect, deletedb{NC}

This command group provides mongo "database" level commands, allowing
connection to a new database, deletion of an existing database, and
listing all existing databases.

""",
)
def database():
    pass


database.add_command(connect.connect)
database.add_command(showAll.showAll)
database.add_command(deleteDB.deleteDB)
