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
from pfmongo.models import responseModel, fsModel
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
import asyncio
from asyncio import get_event_loop
from pydantic import BaseModel

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


class ClickResult(BaseModel):
    exit_code: int
    output: str
    # Add other fields if needed


async def invoke_click_async(app, args: list[str], **kwargs) -> ClickResult:
    """
    Asynchronously invoke a Click command.

    :param app: The Click application.
    :param args: List of command arguments.
    :param kwargs: Additional keyword arguments for CliRunner.invoke.
    :return: A ClickResult instance with the command's result.
    """
    loop = asyncio.get_running_loop()
    runner = CliRunner()
    result = await loop.run_in_executor(
        None, lambda: runner.invoke(app, args, **kwargs)
    )
    return ClickResult(exit_code=result.exit_code, output=result.output)


async def smash_output_async(command: str) -> str:
    """
    Asynchronous version of smash_output.

    :param command: The command string to process.
    :return: The output of the command.
    """
    output: str = meta_parse(command)
    if not output:
        result: ClickResult = await invoke_click_async(
            __main__.app, command.split(), color=True
        )
        output = result.output
    return output


async def smash_execute_async(
    command: str,
    f: Optional[Callable[[str, list[str]], subprocess.CompletedProcess]] = None,
) -> Union[bytes, str]:
    """
    Asynchronous version of smash_execute.

    :param command: The command string to process.
    :param f: Optional callable to handle piped commands.
    :return: Result of the command execution.
    """
    cmdpart: list[str] = pipe_split(command)
    smash_ret: str = await smash_output_async(cmdpart[0])
    result: str = smash_ret

    if len(cmdpart) > 1 and f:
        # Handle potential blocking operation in a separate thread
        loop = asyncio.get_running_loop()
        process: subprocess.CompletedProcess = await loop.run_in_executor(
            None, lambda: f(smash_ret, cmdpart)
        )
        result = f"exec: '{process.args}', returncode: {process.returncode}"
        result = ""

    return result


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


async def smash_executeAsync(
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


async def state_getModel(options: Namespace) -> responseModel.mongodbResponse:
    return await state.showAll_asModel(driver.settmp(options, [{"beQuiet": True}]))


async def cwd(options: Namespace) -> Path:
    model: responseModel.mongodbResponse = await state_getModel(options)
    if model.message == "/":
        return Path("/")
    else:
        return Path("/" + model.message)


async def prompt_get(options: Namespace) -> str:
    promptDo: fsModel.cdResponse = await prompt.prompt_do(
        await prompt.options_add(options)
    )
    pathColor: str = promptDo.message
    return f"{CY}({settings.mongosettings.MD_sessionUser}@smash){NC}{pathColor}$>"


async def command_get(options: Namespace, **kwargs) -> str:
    userInput: str = await tabc.userInput_get(options, **kwargs)
    fscmd: str = f"{userInput}".strip()
    # pudb.set_trace()
    return fscmd


def sync_command_get(options: Namespace, **kwargs) -> str:
    return asyncio.run(command_get(options, **kwargs))


def meta_parse(command: str) -> str:
    output: str = ""
    if "quit" in command.lower() or "exit" in command.lower():
        sys.exit(0)
    if "banner" in command.lower():
        output = introbanner_generate()
    if "fortune" in command.lower():
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
    loop: asyncio.AbstractEventLoop = get_event_loop()
    while True:
        command_str: str = loop.run_until_complete(command_get(options))
        print(smash_execute(command_parse(command_str), pipe_handler))
