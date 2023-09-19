from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
from    pfmisc      import  Colors  as C
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

try:
    from    dbop    import  connect, showAll
except:
    from    .dbop   import  connect, showAll


@click.group(help=f"""
             {GR}database {CY}<cmd>{NC} -- database commands

This command group provides mongo "database" level commands.

""")
def database():
    pass

database.add_command(connect.connect)
database.add_command(showAll.showAll)

