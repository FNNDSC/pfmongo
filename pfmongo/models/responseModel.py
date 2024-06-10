str_description = """

    The data models/schemas for the PACS QR collection.

"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from pathlib import Path
from pfmongo.config import settings


class stateResponse(BaseModel):
    database: str = ""
    collection: str = ""
    app: settings.App = settings.appsettings
    mongo: settings.Mongo = settings.mongosettings


class mongodbResponse(BaseModel):
    """The response model from the mongodb server"""

    status: bool = False
    message: str = ""
    response: dict = {}
    exitCode: int = 0


# Connection status returns


class databaseConnectStatus(BaseModel):
    status: bool = False
    connected: bool = False
    existsAlready: bool = False
    error: str = ""


class collectionConnectStatus(BaseModel):
    status: bool = False
    connected: bool = False
    existsAlready: bool = False
    elements: int = 0
    error: str = ""


# API connection returns


class databaseDesc(BaseModel):
    status: bool = False
    otype: str = "database"
    host: str = ""
    port: int = -1
    name: str = ""
    info: databaseConnectStatus = databaseConnectStatus()


class collectionDesc(BaseModel):
    status: bool = False
    database: databaseDesc = databaseDesc()
    otype: str = "collection"
    databaseName: str = ""
    name: str = ""
    fullName: str = ""
    info: collectionConnectStatus = collectionConnectStatus()


# API usage returns


class showAllDBusage(BaseModel):
    """response for getting a list of all databases in a mongoDB"""

    status: bool = False
    otype: str = "accessing database names"
    databaseNames: list = []
    info: databaseConnectStatus = databaseConnectStatus()


class showAllcollectionsUsage(BaseModel):
    """response for getting a list of all collections in a database"""

    status: bool = False
    otype: str = "accessing collection names"
    collectionNames: list = []
    info: databaseConnectStatus = databaseConnectStatus()


class databaseNamesUsage(BaseModel):
    status: bool = False
    otype: str = "accessing database names"
    databaseNames: list = []
    info: databaseConnectStatus = databaseConnectStatus()


class collectionNamesUsage(BaseModel):
    status: bool = False
    otype: str = "accessing collection names"
    collectionNames: list = []
    info: databaseConnectStatus = databaseConnectStatus()


class DocumentAddUsage(BaseModel):
    """response for adding a document to a collection"""

    status: bool = False
    otype: str = "adding document"
    documentName: str = ""
    document: dict = {}
    resp: dict = {}
    collection: collectionDesc = collectionDesc()


class DocumentDeleteUsage(BaseModel):
    """response for deleting a document from a collection"""

    status: bool = False
    otype: str = "deleting document"
    documentName: str = ""
    document: dict = {}
    resp: dict = {}
    collection: collectionDesc = collectionDesc()


class CollectionDeleteUsage(BaseModel):
    """response for deleting a collection from a database"""

    status: bool = False
    otype: str = "deleting collection"
    collectionName: str = ""
    resp: dict = {}
    collection: collectionDesc = collectionDesc()


class dbDeleteUsage(BaseModel):
    """response for deleting a database from a mongo server"""

    status: bool = False
    otype: str = "deleting collection"
    dbName: str = ""
    resp: dict = {}
    db: databaseDesc = databaseDesc()


class DocumentListUsage(BaseModel):
    """response for listing all documents from a collection"""

    status: bool = False
    otype: str = "listing all documents"
    documentField: str = ""
    documentList: list = []
    resp: dict = {}
    collection: collectionDesc = collectionDesc()


class DocumentSearchUsage(DocumentListUsage):
    """response for listing all documents from a collection"""

    otype: str = "searching all documents"


class DocumentGetUsage(BaseModel):
    """response for getting adding a document from a collection"""

    status: bool = False
    otype: str = "getting document"
    documentName: str = ""
    document: dict = {}
    resp: dict = {}
    collection: collectionDesc = collectionDesc()
