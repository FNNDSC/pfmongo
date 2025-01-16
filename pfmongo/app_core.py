"""
Module for defining and registering the main Click application commands.

This module isolates the definition of the Click `app` and the registration
of all subcommands, providing a centralized and decoupled implementation
for the CLI application.
"""

import re
import click
from argparse import Namespace
from pfmongo import env
from pfmongo.pfmongo import options_initialize
from pfmongo.commands import database, collection, fs, state, document

# Global options namespace
options: Namespace = Namespace()


def namespace_pubattribs(space: Namespace) -> list[str]:
    """
    Retrieve public attributes from a Namespace object.

    :param space: The Namespace object to analyze.
    :return: A list of public attribute names.
    """
    attributes: list[str] = re.findall(r"\b([A-Za-z][A-Za-z_0-9]*)=", str(space))
    return attributes


@click.group(cls=env.CustomGroup, help="A client for interacting with MongoDB.")
@click.option("--man", is_flag=True, help="Show more detail about core OPTIONS.")
@click.option("--version", is_flag=True, help="Show program version.")
@click.pass_context
def app(ctx: click.Context, man: bool, version: bool) -> int:
    """
    Define the main Click application.

    This function sets up the CLI entry point using Click, allowing
    the registration of subcommands and providing base options like
    `--man` and `--version`. It also initializes and attaches the
    global `options` Namespace.

    :param ctx: The Click context object.
    :param man: Flag to show manual details.
    :param version: Flag to show version information.
    :return: 0 on success or an error code on failure.
    """
    global options

    # Initialize options if not already set
    if not namespace_pubattribs(options):
        options = options_initialize()

    # Attach options to the Click context
    ctx.obj = {}
    ctx.obj["options"] = options

    # Placeholder for tracking the invoked subcommand
    subcommand: str | None = click.get_current_context().invoked_subcommand

    return 0


# Register all commands
app.add_command(database.database)
app.add_command(collection.collection)
app.add_command(fs.fs)
app.add_command(state.state)
app.add_command(document.document)


# Import and register smash dynamically to avoid circular import
def register_smash() -> None:
    """
    Dynamically register the `smash` command to avoid circular imports.
    """
    from pfmongo.commands.smash import smash

    app.add_command(smash)


register_smash()
