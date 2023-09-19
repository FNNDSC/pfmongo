from    argparse        import Namespace
from    pfmongo         import driver, pfmongo
from    pfmongo.pfmongo import package_CLIfull, package_argsSynopsisFull, package_argSynopsisSelf
import  pudb
from    pfmisc          import  Colors as C
import  os, sys

try:
    from    .               import __pkg, __version__
except:
    from pfmongo            import __pkg, __version__

NC  = C.NO_COLOUR


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

def synopsis_print(summary:bool = False) -> int:
    scriptName:str          = os.path.basename(sys.argv[0])
    print(C.CYAN + '''
    NAME
        ''', end = '' + NC)
    print(scriptName)
    print(C.CYAN + '''
    CORE SYNPOSIS
        ''' + NC, end = '')
    print(scriptName + pfmongo.package_CLIfull)
    print(C.CYAN + '''
    DESCRIPTION ''' + NC, end = '')
    print(pfmongo.package_coreDescription)

    if summary: return 1
    print(C.CYAN + '''
    ARGS''' + NC, end="")
    print(pfmongo.package_argsSynopsisFull)
    return 2

def coreOptions_show(options:Namespace) -> bool:
    ret:bool    = False
    if options.man or options.version:
        ret     = True
    return ret

def versionAndName_print() -> int:
    print("Name:    ", end="")
    print(C.LIGHT_GREEN + f'{__pkg.name}' + NC)
    print("Version: ", end="")
    print(C.LIGHT_CYAN + f'{__version__}\n')
    return 1

def coreManpage_print() -> int:
    print(f'''
          {C.GREEN}{str_title}
          {str_heading}{NC}
          ''')
    summary:bool    = False
    return synopsis_print(summary)

def man(options:Namespace) -> int:
    #pudb.set_trace()
    if options.version:
        return versionAndName_print()
    if options.man:
        return coreManpage_print()
    return 0
