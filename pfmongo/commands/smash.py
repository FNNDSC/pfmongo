import click
import pudb
from typing import Any, Optional, Callable, Union
import sys
from tabulate import tabulate
from argparse import Namespace
from pfmongo import driver, env
from pfmongo.commands.state import showAll as state
from pfmisc import Colors as C
from pfmongo.models import responseModel
from click.testing import CliRunner
from asyncio import get_event_loop
from pathlib import Path
from fortune import fortune
from pfmongo.config import settings
import subprocess
import asyncio
from pydantic import BaseModel
from pfmongo.commands.slib import tabc
import pfmongo.commands.fop.prompt as prompt

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


def get_app():
    """
    Retrieve the Click application instance.

    This prevents circular imports by delaying the import of `app` until runtime.

    :return: The Click application instance.
    """
    from pfmongo.app_core import app

    return app


def pipe_split(command: str) -> list[str]:
    """
    Split a command string by the pipe (|) character.

    :param command: The command string to split.
    :return: A list containing the split components.
    """
    parts: list[str] = command.split("|", 1)
    return parts


def smash_output(command: str) -> str:
    """
    Execute a command and capture its output.

    :param command: The command string to execute.
    :return: The output of the command execution.
    """
    output: str = meta_parse(command)
    if not output:
        ret = CliRunner().invoke(get_app(), command.split(), color=True)
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
            get_app(), command.split(), color=True
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
    """
    Execute a command synchronously.

    :param command: The command string to execute.
    :param f: Optional callable to handle piped commands.
    :return: The result of the command execution.
    """
    cmdpart: list[str] = pipe_split(command)
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
    """
    Another asynchronous execution method.

    :param command: The command string to process.
    :param f: Optional callable to handle piped commands.
    :return: The result of the command execution.
    """
    cmdpart: list[str] = pipe_split(command)
    smash_ret: str = smash_output(cmdpart[0])
    result: str = smash_ret
    if len(cmdpart) > 1 and f:
        process: subprocess.CompletedProcess = f(smash_ret, cmdpart)
        result = f"exec: '{process.args}', returncode: {process.returncode}"
        result = ""
    return result


def pipe_handler(
    previous_input: str, cmdpart: list[str]
) -> subprocess.CompletedProcess:
    """
    Handle piped shell commands.

    :param previous_input: Input string from the previous command.
    :param cmdpart: List of command parts.
    :return: A completed subprocess process.
    """
    cmds = [c.strip() for c in cmdpart]
    shell_command = "|".join(cmds[1:])
    return subprocess.run(
        shell_command, input=previous_input, shell=True, capture_output=False, text=True
    )


def command_parse(command: str) -> str:
    """
    Parse a command string and prepend "fs" if it matches known commands.

    :param command: The command string.
    :return: The parsed command string.
    """
    fscall = [s for s in fscommand if command.lower().startswith(s)]
    if fscall:
        command = f"fs {command}"
    if command == "help":
        command = "fs --help"
    return command


async def state_getModel(options: Namespace) -> responseModel.mongodbResponse:
    """
    Fetch the current MongoDB state model asynchronously.

    :param options: Namespace containing CLI options.
    :return: The MongoDB state model.
    """
    return await state.showAll_asModel(driver.settmp(options, [{"beQuiet": True}]))


async def cwd(options: Namespace) -> Path:
    """
    Get the current working directory based on MongoDB state.

    :param options: Namespace containing CLI options.
    :return: The current working directory as a Path object.
    """
    model = await state_getModel(options)
    if model.message == "/":
        return Path("/")
    return Path("/" + model.message)


async def prompt_get(options: Namespace, context: str = "smash") -> str:
    """
    Generate a shell prompt string based on the current state.

    :param options: Namespace containing CLI options.
    :param context: Optional string representing the shell context (default: "smash").
    :return: The formatted shell prompt string.
    """
    promptDo = await prompt.prompt_do(await prompt.options_add(options))
    pathColor = promptDo.message
    return f"{CY}({settings.mongosettings.MD_sessionUser}@{context}){NC}{pathColor}$>"


async def command_get(options: Namespace, **kwargs) -> str:
    """
    Asynchronously fetch user input for commands.

    :param options: Namespace containing CLI options.
    :param kwargs: Additional keyword arguments for input handling.
    :return: The user input as a string.
    """
    userInput = await tabc.userInput_get(options, **kwargs)
    return userInput.strip()


def sync_command_get(options: Namespace, **kwargs) -> str:
    """
    Synchronously fetch user input for commands.

    :param options: Namespace containing CLI options.
    :param kwargs: Additional keyword arguments for input handling.
    :return: The user input as a string.
    """
    return asyncio.run(command_get(options, **kwargs))


def meta_parse(command: str) -> str:
    """
    Parse meta commands like "quit", "banner", or "fortune".

    :param command: The command string.
    :return: Parsed output if the command matches; otherwise, an empty string.
    """
    if "quit" in command.lower() or "exit" in command.lower():
        sys.exit(0)
    if "banner" in command.lower():
        return introbanner_generate()
    if "fortune" in command.lower():
        return env.tabulate_message(fortune(), f"{YL}fortune{NC}")
    return ""


def introbanner_generate() -> str:
    """
    Generate the introductory banner for the shell.

    :return: The formatted banner string.
    """
    title = f"{CY}s{YL}imple pf{CY}m{YL}ongo{NC} {CY}a{YL}pplication {CY}sh{YL}ell{NC}"
    banner = f"""
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
{CY}░███████╗███╗░░░███╗░█████╗░███████╗██╗░░██╗██╗░{NC}
{CY}░██╔════╝████╗░████║██╔══██╗██╔════╝██║░░██║██║░{NC}
{CY}░███████╗██╔████╔██║███████║███████╗███████║██║░{NC}
{CY}░╚════██║██║╚██╔╝██║██╔══██║╚════██║██╔══██║╚═╝░{NC}
{CY}░███████║██║░╚═╝░██║██║░░██║███████║██║░░██║██╗░{NC}
{CY}░╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░{NC}
{CY}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{NC}
"""
    intro = f"""
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
    """
    Launch the shell interface for running commands.

    :param ctx: Click context.
    :param prompt: Flag to display the CFS prompt.
    """
    print(introbanner_generate())
    options = ctx.obj["options"]
    loop = get_event_loop()
    while True:
        command_str = loop.run_until_complete(command_get(options))
        print(smash_execute(command_parse(command_str), pipe_handler))
