from pfmongo import pfmongo
from pfmongo.__main__ import main
import os

from pfmongo.commands.dbop import connect as database
from pfmongo.commands.clop import connect as collection, showAll as colShow, deleteCol
from pfmongo.models import responseModel

os.environ["XDG_CONFIG_HOME"] = "/tmp"


def DB_connect(DB: str = "testDB") -> int:
    return database.sync_connectTo_asInt(
        database.options_add(DB, pfmongo.options_initialize())
    )


def test_collection_connect_moduleAsInt() -> None:
    """connect to a collection "testCollection" using a module call with an int return"""
    DB_connect()
    ret: int = collection.sync_connectTo_asInt(
        collection.options_add("testCollection", pfmongo.options_initialize())
    )
    assert ret == 0


def test_collection_connect_main(capsys) -> None:
    """connect to a collection via click"""
    ret: int = 0
    DB_connect()
    try:
        ret = main("collection connect testCollection".split())
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert 'Successfully connected collection to "testCollection"' in captured.out


def test_collection_connect_moduleAsModel() -> None:
    """connect to a collection "testCollection" using a module call with model return"""

    DB_connect()
    ret: responseModel.mongodbResponse = collection.sync_connectTo_asModel(
        collection.options_add("testCollection", pfmongo.options_initialize())
    )
    assert "Successfully" in ret.message


def test_collection_showall_main(capsys) -> None:
    """show all collections via click"""
    ret: int = 0
    DB_connect("admin")
    try:
        ret = main("--useDB admin collection showall".split())
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert "system" in captured.out


def test_collection_showall_moduleAsInt() -> None:
    """show all collections using a module call with an int return"""

    DB_connect("admin")
    ret: int = colShow.sync_showAll_asInt(
        colShow.options_add(pfmongo.options_initialize())
    )
    assert ret == 0


def test_collection_showAll_moduleAsModel() -> None:
    """show all collections using a module call with model return"""
    DB_connect("admin")
    ret: responseModel.mongodbResponse = colShow.sync_showAll_asModel(
        colShow.options_add(pfmongo.options_initialize())
    )
    assert "system" in ret.message


def test_collection_delete_main(capsys) -> None:
    """delete collection via click"""
    ret: int = 0
    try:
        ret = main(
            "--useCollection testCollection collection deletecol testCollection".split()
        )
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert "Successfully" in captured.out


def test_collection_delete_moduleAsInt() -> None:
    """delete databases using a module call with an int return"""

    ret: int = deleteCol.sync_collectiondel_asInt(
        deleteCol.options_add("testCollection", pfmongo.options_initialize())
    )
    assert ret == 0


def test_collection_delete_moduleAsModel() -> None:
    """show all databases using a module call with model return"""

    ret: responseModel.mongodbResponse = deleteCol.sync_collectiondel_asModel(
        deleteCol.options_add("testCollection", pfmongo.options_initialize())
    )

    assert "Successfully" in ret.message
