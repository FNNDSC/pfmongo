str_description = """

    The data models/schemas for the PACS QR collection.

"""

from logging import info
from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path

class mongodbResponse(BaseModel):
    """The model returned internally"""
    status:bool                     = False
    message:str                     = ''
    response:dict                   = {}

class databaseConnectStatus(BaseModel):
    connected:bool                  = False
    existsAlready:bool              = False
    error:str                       = ""

class collectionConnectStatus(BaseModel):
    connected:bool                  = False
    existsAlready:bool              = False
    elements:int                    = 0
    error:str                       = ""

class databaseNamesUsage(BaseModel):
    otype:str                       = "accessing database names"
    databaseNames:list              = []
    info:databaseConnectStatus      = databaseConnectStatus()

class collectionNamesUsage(BaseModel):
    otype:str                       = "accessing collection names"
    databaseNames:list              = []
    info:collectionConnectStatus    = collectionConnectStatus()

class databaseDesc(BaseModel):
    otype:str                       = "database"
    host:str                        = ""
    port:int                        = -1
    name:str                        = ""
    info:databaseConnectStatus      = databaseConnectStatus()

class collectionDesc(BaseModel):
    otype:str                       = "collection"
    databaseName:str                = ""
    name:str                        = ""
    fullName:str                    = ""
    info:collectionConnectStatus    = collectionConnectStatus()

class time(BaseModel):
    """A simple model that has a time string field"""
    time                                : str

