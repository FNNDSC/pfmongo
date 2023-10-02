str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path
from    pfmongo.config      import settings

class stateResponse(BaseModel):
    database:str                    = ""
    collection:str                  = ""
    app:settings.App                = settings.appsettings
    mongo:settings.Mongo            = settings.mongosettings

class mongodbResponse(BaseModel):
    """The response model from the mongodb server"""
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
    collectionNames:list            = []
    info:databaseConnectStatus      = databaseConnectStatus()

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

