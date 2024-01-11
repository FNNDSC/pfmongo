from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
from    pfmisc      import  Colors  as C
import  click
import  pudb
from    pfmongo.commands.dbop   import connect, showAll, deleteDB


NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.group(help=f"""
             {GR}database {CY}<cmd>{NC} -- database commands

This command group provides mongo "database" level commands.

""")
def database():
    pass

database.add_command(connect.connect)
database.add_command(showAll.showAll)
database.add_command(deleteDB.deleteDB)
