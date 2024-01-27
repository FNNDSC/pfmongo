str_description = """

    Some data models/schemas.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path

class messageType(Enum):
    """ message type/level """
    INFO    = 1
    ERROR   = 2

class loggingType(Enum):
    """ logging type """
    CONSOLE = 1
    NDJSON  = 2

class fsPath(BaseModel):
    path:Path       = Path("")
    status:bool     = False
    error:str       = ""

class time(BaseModel):
    """A simple model that has a time string field"""
    time                                : str

