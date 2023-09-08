#!/usr/bin/env python3
#
# (c) 2023+ Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

__version__ = "0.9.9"

import sys, os

from    pfmongo             import pfmongo
from    pfmongo.pfmongo     import parser_setup, parser_interpret, parser_JSONinterpret

try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

import  asyncio
from    asyncio             import AbstractEventLoop

from    argparse            import RawTextHelpFormatter
from    argparse            import ArgumentParser, Namespace
import  pudb
from    pfmisc              import Colors as C
from    typing              import Any, Literal
import  json
import  re
NC =  C.NO_COLOUR

str_title:str = r'''

           $$$$$$\
          $$  __$$\
 $$$$$$\  $$ /  \__|$$$$$$\$$$$\   $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\
$$  __$$\ $$$$\     $$  _$$  _$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\
$$ /  $$ |$$  _|    $$ / $$ / $$ |$$ /  $$ |$$ |  $$ |$$ /  $$ |$$ /  $$ |
$$ |  $$ |$$ |      $$ | $$ | $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |
$$$$$$$  |$$ |      $$ | $$ | $$ |\$$$$$$  |$$ |  $$ |\$$$$$$$ |\$$$$$$  |
$$  ____/ \__|      \__| \__| \__| \______/ \__|  \__| \____$$ | \______/
$$ |                                                  $$\   $$ |
$$ |                                                  \$$$$$$  |
\__|                                                   \______/
'''


str_heading:str = f"""
                        python (pf) monogodb client and module

"""

def synopsis(ab_shortOnly = False) -> None:
    scriptName:str          = os.path.basename(sys.argv[0])
    print(C.CYAN + '''
    NAME
        ''', end = '' + NC)
    print(scriptName)
    print(C.CYAN + '''
    SYNPOSIS
        ''' + NC, end = '')
    print(scriptName + pfmongo.package_CLIfull)
    print(C.CYAN + '''
    DESCRIPTION ''' + NC, end = '')
    print(pfmongo.package_description)

    if ab_shortOnly: return
    print(C.CYAN + '''
    ARGS''' + NC, end="")
    print(pfmongo.package_argsSynopsisFull)

def earlyExit_check(args:Namespace) -> int:
    """
    Check if version/man page are required, and if so service
    and return

    Args:
        args (Namespace): The CLI namespace

    Returns:
        int: 0 -- continue
             1 -- exit
    """
    if args.man:
        print(C.GREEN + str_title)
        str_help:str    = ""
        if args.man:    synopsis(False)
        else:           synopsis(True)
        return 1
    if args.b_version:
        print("Name:    ", end="")
        print(C.LIGHT_CYAN + f'{__pkg.name}' + NC)
        print("Version: ", end="")
        print(C.LIGHT_GREEN + f'{__version__}\n')
        return 1
    return 0

def main(argv=None) -> Literal[1, 0]:

    # pudb.set_trace()
    # Preliminary setup
    parser:ArgumentParser       = parser_setup(
                                    'A client for interacting with monogo DBs'
                                )
    options:Namespace           = parser_interpret(parser, argv)
    if earlyExit_check(options): return 1

    # Create the mongodb object
    mongodb:pfmongo.Pfmongo     = pfmongo.Pfmongo(options)

    # and run it!
    loop:AbstractEventLoop      = asyncio.get_event_loop()
    loop.run_until_complete(mongodb.service())

    print(mongodb.responseData.model_dump_json())

    return 0

if __name__ == "__main__":
    sys.exit(main())
