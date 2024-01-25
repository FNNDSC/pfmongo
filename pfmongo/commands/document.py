from    pfmongo     import  env
from    pfmisc      import  Colors  as C
from    pfmongo.commands.docop import add, delete, search, showAll, get
import  click
import  pudb

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

@click.group(cls = env.CustomGroup, help=f"""
commands suitable for documents: {GR}add, delete, search, showall, get{NC}

This command group provides mongo "document" level commands.

""")
def document():
    pass

document.add_command(add.add)
document.add_command(delete.delete)
document.add_command(search.search)
document.add_command(showAll.showAll)
document.add_command(get.get)
