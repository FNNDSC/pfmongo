from argparse import Namespace
from typing import Any, List, TypedDict, Mapping, Optional
from pydantic import BaseModel, Field

import json
from datetime import datetime
from pathlib import Path

import sys
import shutil
import pudb

import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo import results

from pfmongo.config import settings
from pfmongo.models import responseModel
from pfmongo import env

from motor import motor_asyncio as AIO
from motor.core import AgnosticCursor
from bson import ObjectId
import hashlib
import copy
import re


class mongoDB:
    def getDB(self) -> AIO.AsyncIOMotorDatabase:
        return self.DB

    async def database_names_get(self) -> responseModel.showAllDBusage:
        resp: responseModel.showAllDBusage = responseModel.showAllDBusage()
        l_DBs: list = []
        error: str = ""
        connected: bool = True
        try:
            l_DBs = await self.Mongo.list_database_names()
        except Exception as e:
            connected = False
            error = f"{e}"
        resp.info.connected = connected
        resp.status = connected
        resp.info.error = error
        resp.databaseNames = l_DBs
        return resp

    async def collection_names_get(self) -> responseModel.showAllcollectionsUsage:
        collection: responseModel.showAllcollectionsUsage = (
            responseModel.showAllcollectionsUsage()
        )
        collection.collectionNames = await self.DB.list_collection_names()
        collection.status = True
        return collection

    async def connectDB(self, DBname: str) -> dict:
        """
        Connect to the DB called <DBname> (or create the DB if it does
        not exist). Return the DB and a bool exist_already/not_exist
        in a dictionary.

        Args:
            DBname (str): the DB name

        Returns:
            dict[str, bool | Database[Any]]: DB -- the database
                                             bool -- False if DB is not yet created
        """
        dbnames: responseModel.showAllDBusage = await self.database_names_get()
        d_ret: dict = {
            "connected": dbnames.info.connected,
            "existsAlready": True if DBname in dbnames.databaseNames else False,
            "DB": self.Mongo[DBname],
            "error": dbnames.info.error,
        }
        return d_ret

    async def db_delete(
        self, dbDelete: responseModel.dbDeleteUsage
    ) -> responseModel.dbDeleteUsage:
        await self.Mongo.drop_database(dbDelete.dbName)
        dbDelete.status = True
        return dbDelete

    def insert_one_response(self, d_resp: dict) -> dict[bool, dict]:
        d_data: dict = {"status": False, "document": d_resp}
        if "acknowledged" in d_resp:
            d_data["status"] = d_resp["acknowledged"]
        return d_data

    async def insert_one(
        self, collection: responseModel.collectionDesc, **kwargs
    ) -> responseModel.DocumentAddUsage:
        # pudb.set_trace()
        insert: responseModel.DocumentAddUsage = responseModel.DocumentAddUsage()
        d_document: dict = {}
        for k, v in kwargs.items():
            if k == "document":
                d_document = v
        insert.document = d_document
        insert.collection = collection
        ld_collection: list = [
            d for d in self.ld_collection if d["name"] == collection.name
        ]
        for d in ld_collection:
            insert.resp = await d["object"].document_add(d_document)
            insert.status = insert.resp["acknowledged"]
            insert.documentName = insert.resp["inserted_id"]
        return insert

    async def delete_one(
        self, collection: responseModel.collectionDesc, **kwargs
    ) -> responseModel.DocumentDeleteUsage:
        delete: responseModel.DocumentDeleteUsage = responseModel.DocumentDeleteUsage()
        id: str = ""
        for k, v in kwargs.items():
            if k == "document":
                id = v
        delete.documentName = id
        delete.collection = collection
        ld_collection: list = [
            d for d in self.ld_collection if d["name"] == collection.name
        ]
        for d in ld_collection:
            delete.resp = await d["object"].document_delete(id)
            delete.status = (
                delete.resp["acknowledged"] if delete.resp["deleted_count"] else False
            )
        return delete

    async def get_one(
        self, collection: responseModel.collectionDesc, **kwargs
    ) -> responseModel.DocumentGetUsage:
        get: responseModel.DocumentGetUsage = responseModel.DocumentGetUsage()
        id: str = ""
        for k, v in kwargs.items():
            if k == "document":
                id = v
        get.documentName = id
        get.collection = collection
        ld_collection: list = [
            d for d in self.ld_collection if d["name"] == collection.name
        ]
        for d in ld_collection:
            get.resp = await d["object"].document_get(id)
            get.status = get.resp["acknowledged"]
        if get.status:
            get.document = get.resp["document"]
            get.resp["document"] = "Read successfully"
        return get

    async def listDocs(
        self, collection: responseModel.collectionDesc, **kwargs
    ) -> responseModel.DocumentListUsage:
        """Note: no differentiation between failed call and empty list"""
        docs: responseModel.DocumentListUsage = responseModel.DocumentListUsage()
        field: str = ""
        for k, v in kwargs.items():
            if k == "field":
                field = v
        docs.documentField = field
        docs.collection = collection
        ld_collection: list = [
            d for d in self.ld_collection if d["name"] == collection.name
        ]
        for d in ld_collection:
            docs.resp = await d["object"].document_list(field)
            docs.status = docs.resp["acknowledged"]
        if docs.status:
            docs.documentList = docs.resp["find_list"]
            docs.resp["find_list"] = "Listed successfully"
        docs.status = True
        return docs

    async def searchDocs(
        self, collection: responseModel.collectionDesc, **kwargs
    ) -> responseModel.DocumentSearchUsage:
        docs: responseModel.DocumentSearchUsage = responseModel.DocumentSearchUsage()
        field: str = ""
        searchFor: list = []
        for k, v in kwargs.items():
            if k == "searchFor":
                searchFor = v
            if k == "field":
                field = v
        docs.documentField = field
        docs.collection = collection
        ld_collection: list = [
            d for d in self.ld_collection if d["name"] == collection.name
        ]
        for d in ld_collection:
            docs.resp = await d["object"].document_search(searchFor, field)
            docs.status = docs.resp["acknowledged"]
        if docs.status:
            docs.documentList = docs.resp["find_list"]
            docs.resp["find_list"] = "Listed successfully"
        return docs

    def collection_serialize(self) -> responseModel.collectionDesc:
        resp: responseModel.collectionDesc = responseModel.collectionDesc()
        return resp

    async def connectCol(self, name: str) -> dict:
        colObj: mongoCollection = mongoCollection(self)
        return {
            "name": name,
            "collection": await colObj.connect(name),
            "object": colObj,
            "interface": self.Mongo[name],
        }

    async def collection_delete(self, name: str) -> responseModel.CollectionDeleteUsage:
        # pudb.set_trace()
        resp: responseModel.CollectionDeleteUsage = (
            responseModel.CollectionDeleteUsage()
        )
        resp.collectionName = name
        l_names = [x["name"] for x in self.ld_collection]
        if name not in l_names:
            resp.resp["error"] = "collection not found"
        else:
            lookup: dict = {}
            lookupOrNone: dict | None = next(
                (i for i in self.ld_collection if i["name"] == name), None
            )
            if lookupOrNone:
                lookup = lookupOrNone
                resp.collection = lookup["collection"]
                if not resp.collection.info.error:
                    collectionToRemove: AIO.AsyncIOMotorCollection = lookup[
                        "object"
                    ].d_collection["interface"]
                    await collectionToRemove.drop()
                    self.ld_collection.remove(lookup)
                    resp.status = True
        return resp

    async def collection_connect(self, name: str) -> responseModel.collectionDesc:
        resp: responseModel.collectionDesc = responseModel.collectionDesc()
        l_names = [x["name"] for x in self.ld_collection]
        if name not in l_names:
            self.ld_collection.append(await self.connectCol(name))
            resp = self.ld_collection[-1]["collection"]
        else:
            lookup: responseModel.collectionDesc | None = next(
                (i["collection"] for i in self.ld_collection if i["name"] == name), None
            )
            if lookup:
                resp.collectionDesc = lookup
        return resp

    def __init__(self, **kwargs) -> None:
        """
        The constructor for the mongo data base "object". Each "object"
        is connected to a single mongo database, which can contain a variable
        number of collections (described in a list).

        For "simplicity sake" in this formulation, a new object connection
        is created for each "call"/"use" of this module (i.e. connections
        are single-use).

        Be sure to await the "connect" method on this object after instantiation!

        :param DBname: the string name of the data base within Mongo
        :param settingsMongo: a structure containing the Mongo URI and login
        :return: None -- this is a constructor
        """
        settingsMongo: settings.Mongo = settings.Mongo()
        args: Namespace = Namespace()

        for k, v in kwargs.items():
            if k == "settings":
                settingsMongo = v
            if k == "args":
                args = v

        self.Mongo: AIO.AsyncIOMotorClient = AIO.AsyncIOMotorClient(
            settingsMongo.MD_URI,
            username=settingsMongo.MD_username,
            password=settingsMongo.MD_password,
        )
        self.ld_collection: list[dict] = []
        self.args = args

    def database_serialize(self) -> responseModel.databaseDesc:
        resp: responseModel.databaseDesc = responseModel.databaseDesc()
        # pudb.set_trace()
        resp.host = self.DB.client.HOST
        resp.port = self.DB.client.PORT
        resp.name = str(self.DB.name)
        resp.info.connected = self.d_DBref["connected"]
        resp.info.existsAlready = self.d_DBref["existsAlready"]
        resp.info.error = self.d_DBref["error"]
        resp.info.status = resp.info.connected
        resp.status = resp.info.status
        return resp

    async def connect(self, DBname: str) -> responseModel.databaseDesc:
        self.d_DBref: dict = await self.connectDB(DBname)
        # pudb.set_trace()
        self.DB: AIO.AsyncIOMotorDatabase = self.d_DBref["DB"]
        return self.database_serialize()


class mongoCollection:
    async def search_on(self, d_query: dict) -> list:
        l_hits: list = []
        hits: AIO.AsyncIOMotorCursor = self.collection.find(d_query)
        async for hit in hits:
            l_hits.append(hit)
        # pudb.set_trace()
        return l_hits

    def hash_excludeKeyVal(self, d_hash: dict) -> dict:
        d_hashEx: dict = copy.deepcopy(d_hash)
        keysToClear: list[str] = ["_id", "_date", "_size", "_owner"]
        d_cleared: dict[str, str] = {key: "" for key in keysToClear}
        d_hashEx.update(d_cleared)
        return d_hashEx

    def hash_addToDocument(self, d_doc: dict, l_onlyUsekeys: list = []) -> dict:
        d_newDict: dict = copy.deepcopy(d_doc)
        d_toHash: dict = {}
        if l_onlyUsekeys:
            d_toHash = {k: d_doc[k] for k in l_onlyUsekeys}
        else:
            d_toHash = d_doc
        d_toHash = self.hash_excludeKeyVal(d_toHash)
        d_sorted: dict = dict(sorted(d_toHash.items()))
        hash = hashlib.sha256(str(d_sorted).encode()).hexdigest()
        d_newDict["hash"] = hash
        return d_newDict

    async def is_duplicate(self, d_doc: dict) -> bool:
        b_ret: bool = False
        if "hash" not in d_doc.keys():
            return b_ret
        l_hits: list = await self.search_on({"hash": d_doc["hash"]})
        if len(l_hits):
            b_ret = True
        return b_ret

    def dbcol_add(self, d_resp: dict) -> dict:
        d_resp["database"] = self.DB.name
        d_resp["collection"] = self.collection.name
        return d_resp

    async def document_add(self, d_data: dict) -> dict:
        # pudb.set_trace()
        d_resp: dict = self.dbcol_add(
            {"acknowledged": False, "inserted_id": "-1", "error": ""}
        )
        if self.addHashToDocument:
            d_data = self.hash_addToDocument(d_data)
        if await self.is_duplicate(d_data) and not self.allowDuplicates:
            d_resp["error"] = "Duplicate document hash found."
            d_resp["inserted_id"] = d_data["_id"]
        else:
            resp: results.InsertOneResult = results.InsertOneResult(None, False)
            try:
                resp = await self.collection.insert_one(d_data)
            except Exception as e:
                d_resp["error"] = "%s" % e
            d_resp["acknowledged"] = resp.acknowledged
            d_resp["inserted_id"] = str(resp.inserted_id)
        return d_resp

    async def document_delete(self, id: str) -> dict:
        d_resp: dict = {
            "acknowledged": False,
            "deleted_count": -1,
            "database": "",
            "collection": "",
            "error": "",
        }
        query: dict = {"_id": id}
        raw_result: Mapping[str, int] = {"n": 1}
        resp: results.DeleteResult = results.DeleteResult(raw_result, False)
        for _ in range(0, 2):
            try:
                resp = await self.collection.delete_one(query)
            except Exception as e:
                d_resp["error"] = "%s" % e
            d_resp["acknowledged"] = resp.acknowledged
            d_resp["deleted_count"] = resp.deleted_count
            d_resp["database"] = self.DB.name
            d_resp["collection"] = self.collection.name
            if resp.deleted_count:
                break
            try:
                query = {"_id": ObjectId(id)}
            except Exception as e:
                break
        return d_resp

    async def document_get(self, id: str) -> dict:
        # pudb.set_trace()
        d_resp: dict = {
            "acknowledged": False,
            "document": {},
            "database": "",
            "collection": "",
            "error": "",
        }
        query: dict = {"_id": id}
        for _ in range(0, 2):
            document: Optional[dict[str, Any]] = await self.collection.find_one(query)
            if document:
                document["_id"] = str(document["_id"])
                d_resp["acknowledged"] = True
                d_resp["document"] = document
                d_resp["database"] = self.DB.name
                d_resp["collection"] = self.collection.name
                break
            try:
                query = {"_id": ObjectId(id)}
            except Exception as e:
                d_resp["error"] = f"Could not access {'_id'}: {e}"
        return d_resp

    async def document_list(self, field: str) -> dict:
        # pudb.set_trace()
        d_resp: dict = {"acknowledged": False, "find_list": [], "error": ""}
        query: dict = {field: 1}
        cursor: AgnosticCursor = self.collection.find({}, query)
        async for doc in cursor:
            d_resp["find_list"].append(doc[field])
        if len(d_resp["find_list"]):
            d_resp["acknowledged"] = True
        return d_resp

    async def create_text_index(self):
        """Create a text index on all fields in the collection."""
        await self.collection.create_index([("$**", "text")])

    async def document_search(self, search_terms: list, field: str) -> dict:
        # pudb.set_trace()
        d_resp: dict = {"acknowledged": False, "find_list": [], "error": ""}
        # pudb.set_trace()
        await self.create_text_index()

        regex = "|".join(
            search_terms
        )  # Create a regex pattern that matches any of the search terms
        async for doc in self.collection.find({}):
            for key, value in doc.items():
                if re.search(regex, str(value), re.IGNORECASE):
                    d_resp["find_list"].append(doc["_id"])
                    break

        if not len(d_resp["error"]):
            d_resp["acknowledged"] = True
        return d_resp

    async def collectionNames_list(self, cursor: AIO.AsyncIOMotorCursor) -> list:
        l_collection: list = []
        async for name in cursor:
            l_collection.append(name)
        return l_collection

    async def connectCollection(self, collection: str) -> dict:
        """
        Connect to the collection called <collection> (or create the
        collection if it does not exist). Return the collection and a
        bool exist_already/not_exist in a dictionary.

        :param mongocollection: the name of the collection
        :return: a dictionary with the collection, an element count, and
                    a status
        """
        error: str = ""
        connected: bool = True
        l_collection: list = []
        try:
            l_collection = await self.DB.list_collection_names()
        except Exception as e:
            # pudb.set_trace()
            error = f"{e}"
            connected = False
        d_ret: dict = {
            "connected": connected,
            "exists": True if collection in l_collection else False,
            "interface": self.DB[collection],
            "elements": 0,
            "error": error,
        }
        if d_ret["exists"]:
            filter: dict = {}
            d_ret["elements"] = await d_ret["interface"].count_documents(filter)
        return d_ret

    def __init__(self, DBobject: mongoDB) -> None:
        self.DB: AIO.AsyncIOMotorDatabase = DBobject.getDB()
        self.d_collection: dict = {}
        self.allowDuplicates: bool = DBobject.args.allowDuplicates
        self.addHashToDocument = not DBobject.args.noHashing
        self.donotFlatten = DBobject.args.donotFlatten

    def collection_serialize(self) -> responseModel.collectionDesc:
        # pudb.set_trace()
        resp: responseModel.collectionDesc = responseModel.collectionDesc()
        resp.databaseName = str(self.collection.database.name)
        resp.name = str(self.collection.name)
        resp.fullName = str(self.collection.full_name)
        resp.info.connected = self.d_collection["connected"]
        resp.info.existsAlready = self.d_collection["exists"]
        resp.info.elements = self.d_collection["elements"]
        resp.info.error = self.d_collection["error"]
        resp.info.status = resp.info.connected
        resp.status = resp.info.status
        return resp

    async def connect(self, name: str) -> responseModel.collectionDesc:
        self.d_collection: dict = await self.connectCollection(name)
        self.collection: AIO.AsyncIOMotorCollection = self.d_collection["interface"]
        return self.collection_serialize()
