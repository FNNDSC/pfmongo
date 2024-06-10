from inspect import trace
from pfmongo import pfmongo
from pfmongo.__main__ import main
import os, pudb
from argparse import Namespace
from pfmongo.commands.dbop import connect as database, deleteDB
from pfmongo.commands.clop import connect as collection
from pfmongo.commands.docop import add, get
from pfmongo.commands import smash
from pfmongo.models import responseModel
from pfmongo.config import settings
from pfmongo import driver
import json
import pytest
import asyncio

import tracemalloc

tracemalloc.start()

os.environ["XDG_CONFIG_HOME"] = "/tmp"


@pytest.mark.asyncio
async def DB_connect(DB: str = "testDB") -> int:
    return await database.connectTo_asInt(
        database.options_add(DB, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def collection_connect(col: str = "testCollection") -> int:
    return await collection.connectTo_asInt(
        collection.options_add(col, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def DB_delete(DB: str = "testDB") -> int:
    return await deleteDB.DBdel_asInt(
        deleteDB.options_add(DB, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def smash_do(cmd: str) -> str:
    options: Namespace = pfmongo.options_initialize()
    options.eventLoopDebug = True
    resp: str | bytes = await smash.smash_execute_async(
        smash.command_parse(await smash.command_get(options, noninteractive=cmd))
    )
    if isinstance(resp, str):
        return resp
    if isinstance(resp, bytes):
        return resp.decode()
    return "Invalid response type received"


@pytest.mark.asyncio
async def test_database_showAll() -> None:
    # pudb.set_trace()
    databases: str = await smash_do("database showall")
    assert "admin" in databases


if __name__ == "__main__":
    print("Test document operations")
    pudb.set_trace()
    asyncio.run(test_database_showAll())
