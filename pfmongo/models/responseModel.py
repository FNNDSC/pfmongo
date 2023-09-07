str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path

class mongodbSimple(BaseModel):
    """The simplest mongodb model POST"""
    mongodb                              : str   = ""

class mongodbDelete(BaseModel):
    status                              : bool  = False

class mongodbBoolReturn(BaseModel):
    status                              : bool  = False

class mongodbResponse(BaseModel):
    """The model returned internally"""
    status                              : bool  = False
    message                             : str   = ''
    response                            : dict  = {}

class time(BaseModel):
    """A simple model that has a time string field"""
    time                                : str

