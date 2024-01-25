import  click
import  click
import  pudb
from    typing                  import  Any
import  readline
import  sys
from    tabulate                import tabulate
from    pfmongo                 import driver, env
from    argparse                import Namespace
from    pfmisc                  import Colors as C
from    pfmongo.models          import responseModel
from    typing                  import cast
from    argparse                import Namespace
from    pfmongo.commands.state  import showAll

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

@click.command(cls = env.CustomCommand, help="""
shell interface for running commands

An extremely "simple" pfmongo {YL}shell{NC}. Run commands from a shell-esque
interface that harkens back to the days of /bin/ash!

""")
@click.option('--prompt',
              is_flag=True,
              help='If set, print the CFS cwd as prompt')
@click.pass_context
def pmsh(ctx:click.Context, prompt) -> None:
    print(
    tabulate([[f"Welcome to the {CY}p{YL}f{CY}m{YL}ongo{NC} {CY}s{YL}ystem s{CY}h{YL}ell: {CY}pmsh{NC}"]], tablefmt = 'simple_grid'))
    print(f"""
Enjoy your stay and please remain on the trails!
Oh, and don't feed the wildlife. It's not good
for them.

Type {YL}--help{NC} for a list of commands.

Type {YL}quit{NC} to return to the system.
          """)

    pudb.set_trace()
    options:Namespace                   = ctx.obj['options']
    options.beQuiet                     = True
    model:responseModel.mongodbResponse = responseModel.mongodbResponse()
    prompt                              = ""
    while True:
        model       = showAll.showAll_asModel(options)
        prompt      = f'/{model.message}{GR}>$ {NC}'
        command:str = input(prompt)
        if 'quit' in command.lower() or 'exit' in command.lower():
            sys.exit(0)
        else:
            pass

