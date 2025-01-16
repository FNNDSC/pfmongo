"""
Module for handling the `--man` and `--version` CLI options.

This module provides helper functions to display the manual page and version
information for the pfmongo CLI application.
"""

from argparse import Namespace
from pfmongo import driver, pfmongo
from pfmongo.pfmongo import package_CLIfull, package_argsSynopsisFull
from pfmisc import Colors as C
import os
import sys

NC = C.NO_COLOUR

str_title: str = r"""

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
"""


str_heading: str = f"""
                        python (pf) mongodb client and module

"""


def synopsis_print(summary: bool = False) -> int:
    """
    Print the synopsis of the application, including core usage.

    :param summary: If True, only print a summary.
    :return: Exit code (1 for summary, 2 for full output).
    """
    scriptName: str = os.path.basename(sys.argv[0])
    print(C.CYAN + "\nNAME\n" + NC, end="")
    print(scriptName)
    print(C.CYAN + "\nCORE SYNOPSIS\n" + NC, end="")
    print(scriptName + pfmongo.package_CLIfull)
    print(C.CYAN + "\nDESCRIPTION\n" + NC, end="")
    print(pfmongo.package_coreDescription)

    if summary:
        return 1
    print(C.CYAN + "\nARGS\n" + NC, end="")
    print(pfmongo.package_argsSynopsisFull)
    return 2


def coreOptions_show(options: Namespace) -> bool:
    """
    Check if the `--man` or `--version` options are set.

    :param options: The parsed CLI options.
    :return: True if `--man` or `--version` is set, otherwise False.
    """
    return options.man or options.version


def versionAndName_print() -> int:
    """
    Print the package name and version.

    :return: Exit code (1 for successful version display).
    """
    from pfmongo import __pkg_name__, __version__  # Use updated attributes

    print("Name:    ", end="")
    print(C.LIGHT_GREEN + f"{__pkg_name__}" + NC)
    print("Version: ", end="")
    print(C.LIGHT_CYAN + f"{__version__}" + NC)
    return 1


def coreManpage_print() -> int:
    """
    Print the core manual page.

    :return: Exit code (2 for successful manual display).
    """
    print(f"{C.GREEN}{str_title}{str_heading}{NC}")
    return synopsis_print(summary=False)


def man(options: Namespace) -> int:
    """
    Handle the `--man` and `--version` options.

    :param options: The parsed CLI options.
    :return: Exit code depending on the option:
             1 for `--version`, 2 for `--man`, 0 otherwise.
    """
    if options.version:
        return versionAndName_print()
    if options.man:
        return coreManpage_print()
    return 0
