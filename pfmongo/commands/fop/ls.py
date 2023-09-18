import  click
from    pathlib import  Path
from    pfmisc  import  Colors as C

NC = C.NO_COLOUR
GR = C.LIGHT_GREEN
CY = C.CYAN

@click.command(help=f"""
               {GR}ls {CY}<args>{NC} -- list files

This command lists the objects (files and directories) that are at a given
path. This path can be a directory, in which case possibly multiple objects
are listed, or it can be a single file in which case information about that
single file is listed.

""")
@click.argument('path',
                required = False)
@click.option('--attribs',  required = False,
              help      = 'A comma separated list of file attributes to return/print')
@click.option('--long',
              is_flag   = True,
              help      = 'If set, use a long listing format')
def ls(path:str, attribs:str, long:bool) -> None:
    # pudb.set_trace()
    target:Path     = Path('')
    if path:
        target = Path(path)

