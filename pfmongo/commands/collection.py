from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
from    pfmisc      import  Colors  as C
from    pfmongo.commands.clop   import add, delete, search, showAll, connect
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.group(help=f"""
             {GR}collection {CY}<cmd>{NC} -- collection commands

This command group provides mongo "collection" level commands.

""")
def collection():
    pass

collection.add_command(add.add)
collection.add_command(delete.delete)
collection.add_command(search.search)
collection.add_command(showAll.showAll)
collection.add_command(connect.connect)

