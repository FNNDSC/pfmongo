import  builtins
from    _pytest.capture         import capsys
from    pfmongo                 import pfmongo
from    pfmongo.__main__        import main
from    pfmongo.pfmongo         import options_initialize
from    argparse                import  ArgumentParser, Namespace
import  os
os.environ['XDG_CONFIG_HOME'] = '/tmp'
import  pudb
import  pytest
from    pytest_mock             import mocker
from    datetime                import datetime
import  time
from    typing                  import Any, Callable
from    unittest.mock           import patch

from    pfmongo.commands.clop   import connect, showAll, deleteCol
from    pfmongo.models          import responseModel


def test_database_connect_moduleAsInt(capsys) -> None:
    """ connect to a database "testDB" using a module call with an int return """

    ret:int = connect.connectTo_asInt(connect.options_add("testDB", pfmongo.options_initialize()))
    assert ret == 0

def test_collection_connect_main(capsys) -> None:
    """ connect to a collection via click """
    ret:int     = 0
    try:
        ret     = main(['collection', 'connect', 'testCollection'])
    except SystemExit:
        pass
    captured    = capsys.readouterr()
    assert ret == 0
    assert 'Successfully connected collection to "testCollection"' in captured.out

def test_collection_connect_moduleAsInt(capsys) -> None:
    """ connect to a collection "testCollection" using a module call with an int return """

    ret:int = connect.connectTo_asInt(connect.options_add("testCollection", pfmongo.options_initialize()))
    assert ret == 0

def test_database_connect_moduleAsModel(capsys) -> None:
    """ connect to a collection "testCollection" using a module call with model return """

    ret:responseModel.mongodbResponse = \
        connect.connectTo_asModel(connect.options_add("testCollection", pfmongo.options_initialize()))
    assert 'Successfully' in ret.message

def test_collection_showall_main(capsys) -> None:
    """ show all collections via click """
    ret:int     = 0
    try:
        ret     = main(['collection', 'showall'])
    except SystemExit:
        pass
    captured    = capsys.readouterr()
    assert ret == 0
    assert 'admin' in captured.out

def test_collection_showall_moduleAsInt(capsys) -> None:
    """ show all databases using a module call with an int return """

    ret:int = showAll.showAll_asInt(showAll.options_add(pfmongo.options_initialize()))
    assert ret == 0

def test_collection_showAll_moduleAsModel(capsys) -> None:
    """ show all databases using a module call with model return """

    ret:responseModel.mongodbResponse = \
        showAll.showAll_asModel(showAll.options_add(pfmongo.options_initialize()))
    assert 'admin' in ret.message

def test_collection_delete_main(capsys) -> None:
    """ delete collection via click """
    ret:int     = 0
    try:
        ret     = main(['--useCollection', 'testCollection', 'collection', 'deletecol', 'testCollection'])
    except SystemExit:
        pass
    captured    = capsys.readouterr()
    assert ret == 0
    assert 'Successfully' in captured.out

def test_collection_delete_moduleAsInt(capsys) -> None:
    """ delete databases using a module call with an int return """

    ret:int = deleteCol.collectiondel_asInt(
                deleteCol.options_add("testCollection", pfmongo.options_initialize()))
    assert ret == 0

def test_collection_delete_moduleAsModel(capsys) -> None:
    """ show all databases using a module call with model return """

    ret:responseModel.mongodbResponse = \
        deleteCol.collectiondel_asModel(
                deleteCol.options_add("testCollection", pfmongo.options_initialize()))

    assert 'Successfully' in ret.message
