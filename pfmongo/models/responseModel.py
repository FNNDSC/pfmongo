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

# Connection status returns

class databaseConnectStatus(BaseModel):
    status:bool                     = False
    connected:bool                  = False
    existsAlready:bool              = False
    error:str                       = ""

class collectionConnectStatus(BaseModel):
    status:bool                     = False
    connected:bool                  = False
    existsAlready:bool              = False
    elements:int                    = 0
    error:str                       = ""

# API connection returns

class databaseDesc(BaseModel):
    status:bool                     = False
    otype:str                       = "database"
    host:str                        = ""
    port:int                        = -1
    name:str                        = ""
    info:databaseConnectStatus      = databaseConnectStatus()

class collectionDesc(BaseModel):
    status:bool                     = False
    database:databaseDesc           = databaseDesc()
    otype:str                       = "collection"
    databaseName:str                = ""
    name:str                        = ""
    fullName:str                    = ""
    info:collectionConnectStatus    = collectionConnectStatus()

# API usage returns

class showAllDBusage(BaseModel):
    status:bool                     = False
    otype:str                       = "accessing database names"
    databaseNames:list              = []
    info:databaseConnectStatus      = databaseConnectStatus()

class showAllcollectionsUsage(BaseModel):
    status:bool                     = False
    otype:str                       = "accessing collection names"
    collectionNames:list            = []
    info:databaseConnectStatus      = databaseConnectStatus()

class databaseNamesUsage(BaseModel):
    status:bool                     = False
    otype:str                       = "accessing database names"
    databaseNames:list              = []
    info:databaseConnectStatus      = databaseConnectStatus()

class collectionNamesUsage(BaseModel):
    status:bool                     = False
    otype:str                       = "accessing collection names"
    collectionNames:list            = []
    info:databaseConnectStatus      = databaseConnectStatus()

class DocumentAddUsage(BaseModel):
    status:bool                     = False
    otype:str                       = "adding document"
    documentName:str                = ""
    document:dict                   = {}
    resp:dict                       = {}
    collection:collectionDesc       = collectionDesc()
