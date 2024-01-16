from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
from    pfmisc      import  Colors  as C
from    pfmongo.commands.docop import add, delete, search, showAll, get
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.group(help=f"""
             {GR}document{CY} <cmd>{NC} -- document commands

This command group provides mongo "document" level commands.

""")
def document():
    pass

document.add_command(add.add)
document.add_command(delete.delete)
document.add_command(search.search)
document.add_command(showAll.showAll)
document.add_command(get.get)
