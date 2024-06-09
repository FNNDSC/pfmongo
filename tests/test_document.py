from pfmongo import pfmongo
from pfmongo.__main__ import main
import os, pudb

from pfmongo.commands.dbop import connect as database, deleteDB
from pfmongo.commands.clop import connect as collection
from pfmongo.commands.docop import add, get
from pfmongo.models import responseModel
from pfmongo.config import settings
from pfmongo import driver
import json
import pytest
import asyncio

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
async def test_document_add_asInt() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    retlld: int = await add.documentAdd_asInt(
        add.options_add("examples/lld.json", "lld.json", pfmongo.options_initialize())
    )
    retneuro1: int = await add.documentAdd_asInt(
        add.options_add(
            "examples/neuro1.json", "neuro1.json", pfmongo.options_initialize()
        )
    )
    retneuro2: int = await add.documentAdd_asInt(
        add.options_add(
            "examples/neuro2.json", "neuro2.json", pfmongo.options_initialize()
        )
    )
    retultrasound: int = await add.documentAdd_asInt(
        add.options_add(
            "examples/ultrasound.json", "ultrasound.json", pfmongo.options_initialize()
        )
    )
    assert retlld == 0
    assert retneuro1 == 0
    assert retneuro2 == 0
    assert retultrasound == 0
    await DB_delete()


@pytest.mark.asyncio
async def test_duplicate_add_asInt() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    retlld: int = await add.documentAdd_asInt(
        add.options_add("examples/lld.json", "lld.json", pfmongo.options_initialize())
    )
    assert retlld == 0
    retlld = await add.documentAdd_asInt(
        add.options_add("examples/lld.json", "lld.json", pfmongo.options_initialize())
    )
    assert retlld == 103
    await DB_delete()


@pytest.mark.asyncio
async def test_duplicateID_add_asModel() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    retlld: responseModel.mongodbResponse = await add.documentAdd_asModel(
        add.options_add(
            "examples/lld.json",
            "lld.json",
            pfmongo.options_initialize([{"noHashing": True}]),
        )
    )
    retlld = await add.documentAdd_asModel(
        add.options_add(
            "examples/lld.json",
            "lld.json",
            pfmongo.options_initialize([{"noHashing": True}]),
        )
    )
    assert "Could not add" in retlld.message
    assert not retlld.response["status"]
    assert "E11000 duplicate key" in retlld.response["connect"].resp["error"]
    await DB_delete()


@pytest.mark.asyncio
async def test_duplicateHash_add_asModel() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    retlld: responseModel.mongodbResponse = await add.documentAdd_asModel(
        add.options_add("examples/lld.json", "lld2.json", pfmongo.options_initialize())
    )
    retlld = await add.documentAdd_asModel(
        add.options_add("examples/lld.json", "lld2.json", pfmongo.options_initialize())
    )
    assert "Could not add" in retlld.message
    assert not retlld.response["status"]
    assert "Duplicate document hash found." in retlld.response["connect"].resp["error"]
    await DB_delete()


@pytest.mark.asyncio
async def test_document_get_asInt() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    load: int = await add.documentAdd_asInt(
        add.options_add("examples/lld.json", "lld.json", pfmongo.options_initialize())
    )
    assert load == 0
    read: int = await get.documentGet_asInt(
        get.options_add("lld.json", pfmongo.options_initialize())
    )
    assert read == 0
    await DB_delete()


@pytest.mark.asyncio
async def test_document_get_asModel() -> None:
    await DB_delete()
    await DB_connect()
    await collection_connect()
    load: int = await add.documentAdd_asInt(
        add.options_add("examples/lld.json", "lld.json", pfmongo.options_initialize())
    )
    assert load == 0
    read: responseModel.mongodbResponse = await get.documentGet_asModel(
        get.options_add("lld.json", pfmongo.options_initialize())
    )
    d_read: dict[str, str] = json.loads(read.message)
    assert d_read["_id"] == "lld.json"
    await DB_delete()


@pytest.mark.asyncio
async def test_deleteTestDB() -> None:
    ret: int = await deleteDB.DBdel_asInt(
        deleteDB.options_add("testDB", pfmongo.options_initialize())
    )
    assert ret == 0


if __name__ == "__main__":
    print("Test document operations")
    pudb.set_trace()
    asyncio.run(test_document_get_asModel())
