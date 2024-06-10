import click
from pfmongo import driver, env
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo.models import responseModel
from pathlib import Path
import pudb
import copy

import pfmongo.commands.fop.cd as cd

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
PL = C.PURPLE
YL = C.YELLOW


@click.command(
    cls=env.CustomCommand,
    help=f"""
make-and-cd into a {YL}directory{NC}

SYNOPSIS
{CY}mkcd {YL}<path>{NC}

DESC
The {CY}mkcd{NC} is analogous to a combined "mkdir" and "cd" command. It
"creates a new directory" {YL}path{NC} within a mongodb and performs a
{CY}cd{NC} into that {YL}path{NC}.

In reality this is simply an alias to {CY}cd {YL}--create <path>{NC}

""",
)
@click.pass_context
@click.argument("path", required=False)
def mkcd(ctx: click.Context, path: str) -> int:
    # pudb.set_trace()
    mkdir: bool = True
    return cd.sync_changeDirectory(cd.options_add(path, ctx.obj["options"], mkdir)).code
