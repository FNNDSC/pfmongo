from pathlib import Path
from argparse import Namespace
from typing import Optional
from pfmongo import env
from pfmisc import Colors as C
import click
import pudb

from pfmongo.commands.fop import cd, ls, cat, mkcd, imp, exp, pwd, prompt, rm, sg

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN


def root(options: Namespace) -> Path:
    root: Path = Path()
    RFS: Path = options.thisSession
    splitPoint: str = "_MONGO_"
    si: Optional[int] = next(
        (i for i, segment in enumerate(RFS.parts) if splitPoint in segment), None
    )
    if si is not None:
        root = Path(*list(RFS.parts)[: si + 1])
    return root


@click.group(
    cls=env.CustomGroup,
    help=f"""
commands suitable for "{GR}file system{NC}" abstractions

This command group uses file system (FS) "commands" in the context of a mongodb
allowing for an FS-modeled interface.

""",
)
def fs():
    pass


fs.add_command(ls.ls)
fs.add_command(cat.cat)
fs.add_command(cd.cd)
fs.add_command(mkcd.mkcd)
fs.add_command(imp.imp)
fs.add_command(exp.exp)
fs.add_command(pwd.pwd)
fs.add_command(prompt.prompt)
fs.add_command(rm.rm)
fs.add_command(sg.sg)
