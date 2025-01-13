from pfmongo import pfmongo
from pfmongo.__main__ import main
import os, pudb
from pfmongo.commands.dbop import connect as database, deleteDB
from pfmongo.commands.clop import connect as collection
from pfmongo.commands.docop import add, get
from pfmongo.models import responseModel
from pfmongo.config import settings
import json
import pytest
import asyncio
import uuid

os.environ["XDG_CONFIG_HOME"] = "/tmp"


@pytest.fixture(autouse=True)
async def cleanup():
    """
    Cleanup databases after each test function in this file.
    """
    await DB_delete()
    yield
    await DB_delete()  # Clean up the database after the test runs


@pytest.mark.asyncio
async def DB_connect(DB: str = "testDB") -> int:
    """
    Connect to the specified MongoDB database.
    """
    return await database.connectTo_asInt(
        database.options_add(DB, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def collection_connect(col: str = "testCollection") -> int:
    """
    Connect to the specified MongoDB collection.
    """
    return await collection.connectTo_asInt(
        collection.options_add(col, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def DB_delete(DB: str = "testDB") -> int:
    """
    Delete the specified MongoDB database.
    """
    return await deleteDB.DBdel_asInt(
        deleteDB.options_add(DB, pfmongo.options_initialize())
    )


@pytest.mark.asyncio
async def test_duplicateHash_add_asModel() -> None:
    """
    Test handling duplicate document hashes.
    """
    await DB_delete()
    await DB_connect()
    await collection_connect()
    # pudb.set_trace()
    retlld: responseModel.mongodbResponse = await add.documentAdd_asModel(
        add.options_add("examples/lld.json", "lld2.json", pfmongo.options_initialize())
    )
    retlld = await add.documentAdd_asModel(
        add.options_add("examples/lld.json", "lld3.json", pfmongo.options_initialize())
    )
    print(retlld.response)
    print(retlld.response["connect"].resp)
    print(settings.appsettings)
    assert not retlld.response["status"]
    assert "Duplicate document hash found." in retlld.response["connect"].resp["error"]
    await DB_delete()


if __name__ == "__main__":
    print("Test document duplicate hash detection")
    pudb.set_trace()
    asyncio.run(test_duplicateHash_add_asModel())
