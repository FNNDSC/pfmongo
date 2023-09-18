from    pathlib     import  Path
from    argparse    import  Namespace
from    typing      import  Optional
import  click
import  pudb

try:
    from    fop     import ls, cat, cd, mkdir, imp, exp
except:
    from    .fop    import ls, cat, cd, mkdir, imp, exp


def root(options:Namespace) -> Path:
    root:Path       = Path()
    RFS:Path        = options.thisSession
    splitPoint:str  = '_MONGO_'
    si:Optional[int]= next((i for i, segment in enumerate(RFS.parts) if splitPoint in segment), None)
    if si is not None:
        root        = Path(*list(RFS.parts)[:si + 1])
    return root

@click.group(help="""
                    file system type subcommands

This command group uses file system (FS) "commands" in the context of a mongodb
allowing for an FS-modeled interface.

""")
def fs():
    pass

fs.add_command(ls.ls)
fs.add_command(cat.cat)
fs.add_command(cd.cd)
fs.add_command(mkdir.mkdir)
fs.add_command(imp.imp)
fs.add_command(exp.exp)

