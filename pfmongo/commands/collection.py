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
    from    clop    import  add, delete, search, show
except:
    from    .clop   import  add, delete, search, show


@click.group(help=f"""
             {GR}collection {CY}<cmd>{NC} -- collection commands

This command group provides mongo "collection" level commands

""")
def collection():
    pass

collection.add_command(add.add)
collection.add_command(delete.delete)
collection.add_command(search.search)
collection.add_command(show.show)


