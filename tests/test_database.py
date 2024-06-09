from pfmongo import pfmongo
from pfmongo.__main__ import main

import os

from pfmongo.commands.dbop import connect, showAll, deleteDB
from pfmongo.models import responseModel

os.environ["XDG_CONFIG_HOME"] = "/tmp"


def test_database_connect_main(capsys) -> None:
    """connect to a database via click"""
    ret: int = 0
    try:
        ret = main("database connect testDB".split())
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert 'Successfully connected database to "testDB"' in captured.out


def test_database_connect_moduleAsInt() -> None:
    """connect to a database "testDB" using a module call with an int return"""

    ret: int = connect.sync_connectTo_asInt(
        connect.options_add("testDB", pfmongo.options_initialize())
    )
    assert ret == 0


def test_database_connect_moduleAsModel() -> None:
    """connect to a database "testDB" using a module call with model return"""

    ret: responseModel.mongodbResponse = connect.sync_connectTo_asModel(
        connect.options_add("testDB", pfmongo.options_initialize())
    )
    assert "Successfully" in ret.message


def test_database_showall_main(capsys) -> None:
    """show all databases via click"""
    ret: int = 0
    try:
        ret = main("database showall".split())
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert "admin" in captured.out


def test_database_showall_moduleAsInt() -> None:
    """show all databases using a module call with an int return"""

    ret: int = showAll.sync_showAll_asInt(
        showAll.options_add(pfmongo.options_initialize())
    )
    assert ret == 0


def test_database_showAll_moduleAsModel() -> None:
    """show all databases using a module call with model return"""

    ret: responseModel.mongodbResponse = showAll.sync_showAll_asModel(
        showAll.options_add(pfmongo.options_initialize())
    )
    assert "admin" in ret.message


def test_database_delete_main(capsys) -> None:
    """delete database via click"""
    ret: int = 0
    try:
        ret = main("database deletedb testDB".split())
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert ret == 0
    assert "Successfully" in captured.out


def test_database_delete_moduleAsInt() -> None:
    """delete databases using a module call with an int return"""

    ret: int = deleteDB.sync_DBdel_asInt(
        deleteDB.options_add("testDB", pfmongo.options_initialize())
    )
    assert ret == 0


def test_database_delete_moduleAsModel() -> None:
    """delete database using a module call with model return"""

    ret: responseModel.mongodbResponse = deleteDB.sync_DBdel_asModel(
        deleteDB.options_add("testDB", pfmongo.options_initialize())
    )

    assert "Successfully" in ret.message
