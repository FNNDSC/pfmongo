#!/usr/bin/env python3
#
# (c) 2023+ Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

__version__ = "0.9.9"

import sys

from    pfmongo             import pfmongo
from    pfmongo             import driver
from    pfmongo.commands    import fs
from    pfmongo.pfmongo     import parser_setup, parser_interpret, parser_JSONinterpret

try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

from    argparse            import ArgumentParser, Namespace
import  pudb
from    pfmisc              import Colors as C
from    typing              import Any, Literal
from    pfmongo.config      import settings
from    pfmongo.models      import dataModel
from    pathlib             import Path
import  appdirs
import  click
from    click.formatting    import wrap_text

try:
    from    commands        import  database, collection, fs, man
    from    commands        import  man as manual

except:
    from    .commands       import  database, collection, fs, man
    from    .commands       import  man as manual

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN

options:Namespace               = Namespace()

def sysargv_revamp(newarg:list[str]) ->list[str]:
    """
    Small but crucial method for "revamping" the sys.argv list that
    is passed to the main click function.

    The new list is returned in addition to being set in the sys
    module.

    :param newarg: a string list of "new" arguments
    """
    executable:str              = sys.argv[0]
    sys.argv                    = []
    sys.argv.append(executable)
    sys.argv.extend(newarg)
    return sys.argv

def main(argv:list[str]=[]) -> int:
    """
    The main entry point to the program. Can also be called from Python by
    passing along a "pseudo" argv list of strings (note the first element of
    the list MUST be the executable name).

    The "core" CLI args are processed here.

    This function demonstrates a design pattern that mixes argparse and click
    parsing, hopefully leveraging something of the best of both worlds.

    :param argv: a CLI argv list of strings.
    """
    global options
    # pudb.set_trace()
    add_help:bool               = False
    parser:ArgumentParser       = parser_setup(
                                    'A client for interacting with mongo DBs',
                                    add_help
                                )

    # Should we show (and exit) some man page help?
    options, extra              = parser_interpret(parser, argv)

    # Is this correct?
    if options.DBname:
        settings.mongosettings.MD_DB    = options.DBname
    if settings.mongosettings.MD_DB and not options.DBname:
        options.DBname          = settings.mongosettings.MD_DB
    URI:str                     = settings.mongosettings.MD_URI.\
                                        replace(':', '-').\
                                        replace('/', '')
    options.configPath          = Path(
            appdirs.user_config_dir(appname = __pkg.name)
    )
    options.thisSession         = options.configPath        / \
                                    Path("_MONGO_" + URI)   / \
                                    Path(settings.mongosettings.MD_DB)
    if not settings.mongosettings.MD_sessionUser:
        return driver.complain(f'''
                An 'MD_sessionUser' has not been specified in the environment.
                This variable denotes the "name" of a current user of the service
                and is used to store user specific state data.

                Please set with:

                        export {GR}MD_SESSIONUSER{NC}={CY}yourName{NC}
                ''',
                5,
                dataModel.messageType.ERROR)
    options.sessionUser         = settings.mongosettings.MD_sessionUser
    if man.coreOptions_show(options):
        return man.man(options)

    # the click "app" interprets sys.argv, hence the revamping here
    newargv:list[str]           = sysargv_revamp(extra)

    return(app())

@click.group(help = pfmongo.package_description)
@click.option('--man',
              is_flag   = True,
              help      = 'show more detail about core OPTIONS')
@click.option('--version',
              is_flag   = True,
              help      = 'show program version')
@click.pass_context
def app(ctx:click.Context,
        man:bool, version:bool) -> int:
    """
    The main "app" -- it mostly serves as a point to route to the
    various subcommands and provide some in-line help.

    Note the --man and --version are added as options here only to
    be picked up by the "--help", but they are in fact handled by
    the parent main() method.

    :param ctx: a click "context" -- it is expanded here to transmit additional
                information to subcommands.
    :param man: a CLI --man parameter used to dispatch to the argparse handler
    :return: simply returns a 0:success or <N>:failure
    """

    global options
    ctx.obj                     = {}
    ctx.obj['options']          = options

    subcommand:str|None         = click.get_current_context().invoked_subcommand
    #pudb.set_trace()
    #if subcommand != 'fs':
    #    envCheckFailure:int     = driver.env_failCheck(options)
    #    if envCheckFailure:
    #        return envCheckFailure
    return 0

app.add_command(database.database)
app.add_command(collection.collection)
app.add_command(fs.fs)
#app.add_command(man.man)

