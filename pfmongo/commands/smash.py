import  click
import  click
import  pudb
from    typing                  import  Any
import  readline
import  sys
from    tabulate                import tabulate
from    pfmongo                 import pfmongo, __main__
from    pfmongo                 import driver, env
from    argparse                import Namespace
from    pfmisc                  import Colors as C
from    pfmongo.models          import responseModel
from    typing                  import cast
from    argparse                import Namespace
from    pfmongo.commands.state  import showAll as state
from    click.testing           import CliRunner
from    pathlib                 import Path
import  ast
from    fortune                 import fortune
import  copy

NC  = C.NO_COLOUR
GR  = C.GREEN
CY  = C.CYAN
YL  = C.YELLOW

fscommand:list  = ['ls', 'cat', 'rm', 'cd', 'mkdir', 'imp', 'exp']

def command_parse(command:str) -> str:
    fscall:list = [s for s in fscommand if command.lower().startswith(s)]
    if fscall:
        command = f"fs {command}"
    if command == 'help':
        command = 'fs --help'
    return command

def state_getModel(options:Namespace) -> responseModel.mongodbResponse:
    return state.showAll_asModel(
            driver.settmp(
                          options,
                          [{'beQuiet': True}]
            )
    )

def cwd(options:Namespace) -> Path:
    model:responseModel.mongodbResponse = state_getModel(options)
    if model.message == '/':
        return Path('/')
    else:
        return Path('/' + model.message)

def prompt_get(options:Namespace) -> str:
    model:responseModel.mongodbResponse = state_getModel(options)
    prompt                              = f"{CY}(smash){NC}/{model.message}{GR}>$ {NC}"
    return prompt

def meta_parse(command:str) -> bool:
    b_ret   = False
    if 'quit' in command.lower() or 'exit' in command.lower():
        sys.exit(0)
    if command == 'banner':
        print(introbanner_generate())
        b_ret   = True
    if command == 'fortune':
        print(env.tabulate_message(fortune(), f'{YL}fortune{NC}'))
        b_ret   = True
    return b_ret

def introbanner_generate() -> str:
    title:str   = f"{CY}s{YL}imple pf{CY}m{YL}ongo{NC} {CY}a{YL}pplication {CY}sh{YL}ell{NC}"
    banner:str  = f"""
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
{CY}░███████╗███╗░░░███╗░█████╗░███████╗██╗░░██╗██╗░{NC}
{CY}░██╔════╝████╗░████║██╔══██╗██╔════╝██║░░██║██║░{NC}
{CY}░███████╗██╔████╔██║███████║███████╗███████║██║░{NC}
{CY}░╚════██║██║╚██╔╝██║██╔══██║╚════██║██╔══██║╚═╝░{NC}
{CY}░███████║██║░╚═╝░██║██║░░██║███████║██║░░██║██╗░{NC}
{CY}░╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░{NC}
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
"""
    intro:str   = f"""
Welcome to {CY}smash{NC}, a simple shell to {YL}pfmongo{NC} that
allows you to directly call various subcommands.

If you really want to {CY}smash{NC} things up, the shell allows
you to call the {YL}fs{NC} subcommands without the {YL}fs{NC}, giving
the impression of being in a more standard un*x land.

Some useful commands:
 ▙▄ {YL}--help{NC} for a list of {YL}all{NC} commands.
 ▙▄ {YL}banner{NC} to see this amazing banner again.
 ▙▄ {YL}fortune{NC} since every shell needs this.
 ▙▄ {YL}help{NC} for a list of {YL}fs{NC} commands.
 ▙▄ {YL}quit{NC} or {YL}exit{NC} to return to the system.

Enjoy your stay and please remain on the trails!
Oh, and don't feed the wildlife. It's not good
for them.

Have a {CY}smash{NC}ing good time!
"""
    return env.tabulate_message(banner + intro, title)

@click.command(cls = env.CustomCommand, help="""
shell interface for running commands

An extremely "simple" pfmongo {YL}shell{NC}. Run commands from a shell-esque
interface that harkens back to the days of /bin/ash!

""")
@click.option('--prompt',
              is_flag=True,
              help='If set, print the CFS cwd as prompt')
@click.pass_context
def smash(ctx:click.Context, prompt) -> None:
    print(introbanner_generate())
    # pudb.set_trace()
    options:Namespace                   = ctx.obj['options']
    runner                              = CliRunner()
    model:responseModel.mongodbResponse = responseModel.mongodbResponse()
    while True:
        command:str = command_parse(input(prompt_get(options)))
        if meta_parse(command):
            continue
        ret = runner.invoke(__main__.app, command.split(), color = True)
        print(ret.output)

