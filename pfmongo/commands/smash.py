import click
import click
import pudb
from typing import Any
import readline
import sys
from tabulate import tabulate
from pfmongo import pfmongo, __main__
from pfmongo import driver, env
from argparse import Namespace
from pfmisc import Colors as C
from pfmongo.models import responseModel
from typing import cast
from argparse import Namespace
from pfmongo.commands.state import showAll as state
from click.testing import CliRunner
from pathlib import Path
import ast
from fortune import fortune
import copy
import pfmongo.commands.fop.prompt as prompt
from pfmongo.config import settings
import subprocess
from typing import Optional, Callable, Union

# from    ansi2html               import Ansi2HTMLConverter
from pfmongo.commands.slib import tabc

NC = C.NO_COLOUR
GR = C.GREEN
CY = C.CYAN
YL = C.YELLOW

fscommand: list = [
    "sg",
    "ls",
    "cat",
    "rm",
    "cd",
    "mkcd",
    "imp",
    "exp",
    "prompt",
    "pwd",
    "quit",
    "exit",
    "fortune",
    "banner",
]

fscommand_noArgs: list = ["prompt", "pwd", "quit", "exit"]


def pipe_split(command: str) -> list:
    parts: list[str] = command.split("|", 1)
    return parts


def smash_output(command: str) -> str:
    output: str = meta_parse(command)
    if not output:
        ret = CliRunner().invoke(__main__.app, command.split(), color=True)
        output = ret.output
    return output


def smash_execute(
    command: str,
    f: Optional[Callable[[str, list[str]], subprocess.CompletedProcess]] = None,
) -> Union[bytes, str]:
    cmdpart: list = pipe_split(command)
    smash_ret: str = smash_output(cmdpart[0])
    result: str = smash_ret
    if len(cmdpart) > 1 and f:
        process: subprocess.CompletedProcess = f(smash_ret, cmdpart)
        result = f"exec: '{process.args}', returncode: {process.returncode}"
        result = ""
    return result


def pipe_handler(previous_input: str, cmdpart: list) -> subprocess.CompletedProcess:
    cmds = [c.strip() for c in cmdpart]
    shell_command = "|".join(cmds[1:])
    result: subprocess.CompletedProcess = subprocess.run(
        shell_command, input=previous_input, shell=True, capture_output=False, text=True
    )
    # converter:Ansi2HTMLConverter    = Ansi2HTMLConverter()
    # output:str                      = converter.convert(result.stdout)
    return result


def command_parse(command: str) -> str:
    fscall: list = [s for s in fscommand if command.lower().startswith(s)]
    if fscall:
        command = f"fs {command}"
    if command == "help":
        command = "fs --help"
    return command


def state_getModel(options: Namespace) -> responseModel.mongodbResponse:
    return state.showAll_asModel(driver.settmp(options, [{"beQuiet": True}]))


def cwd(options: Namespace) -> Path:
    model: responseModel.mongodbResponse = state_getModel(options)
    if model.message == "/":
        return Path("/")
    else:
        return Path("/" + model.message)


def prompt_get(options: Namespace) -> str:
    pathColor: str = prompt.prompt_do(prompt.options_add(options)).message
    return f"{CY}({settings.mongosettings.MD_sessionUser}@smash){NC}{pathColor}$>"


def command_get(options: Namespace) -> str:
    userInput: str = tabc.userInput_get(options)
    fscmd: str = f"{userInput}".strip()
    # pudb.set_trace()
    return fscmd


def meta_parse(command: str) -> str:
    output: str = ""
    if "quit" in command.lower() or "exit" in command.lower():
        sys.exit(0)
    if command == "banner":
        output = introbanner_generate()
    if command == "fortune":
        output = env.tabulate_message(fortune(), f"{YL}fortune{NC}")
    return output


def introbanner_generate() -> str:
    title: str = (
        f"{CY}s{YL}imple pf{CY}m{YL}ongo{NC} {CY}a{YL}pplication {CY}sh{YL}ell{NC}"
    )
    banner: str = f"""
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
{CY}░███████╗███╗░░░███╗░█████╗░███████╗██╗░░██╗██╗░{NC}
{CY}░██╔════╝████╗░████║██╔══██╗██╔════╝██║░░██║██║░{NC}
{CY}░███████╗██╔████╔██║███████║███████╗███████║██║░{NC}
{CY}░╚════██║██║╚██╔╝██║██╔══██║╚════██║██╔══██║╚═╝░{NC}
{CY}░███████║██║░╚═╝░██║██║░░██║███████║██║░░██║██╗░{NC}
{CY}░╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░{NC}
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
"""
    intro: str = f"""
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


@click.command(
    cls=env.CustomCommand,
    help="""
shell interface for running commands

An extremely "simple" pfmongo {YL}shell{NC}. Run commands from a shell-esque
interface that harkens back to the days of /bin/ash!

""",
)
@click.option("--prompt", is_flag=True, help="If set, print the CFS cwd as prompt")
@click.pass_context
def smash(ctx: click.Context, prompt) -> None:
    print(introbanner_generate())
    options: Namespace = ctx.obj["options"]
    while True:
        print(smash_execute(command_parse(command_get(options)), pipe_handler))
