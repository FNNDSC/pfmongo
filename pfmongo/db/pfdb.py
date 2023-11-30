from    argparse            import Namespace
from    typing              import Any, List, TypedDict
from    pydantic            import BaseModel, Field

import  json
from    datetime            import datetime
from    pathlib             import Path

import  sys
import  shutil
import  pudb

import  pymongo
from    pymongo             import MongoClient
from    pymongo.database    import Database
from    pymongo.collection  import Collection
from    pymongo             import results

from    pfmongo.config      import settings
from    pfmongo.models      import responseModel

from    motor               import motor_asyncio as AIO

import  hashlib
import  copy

class mongoDB():

    def getDB(self) -> AIO.AsyncIOMotorDatabase:
        return self.DB

    async def database_names_get(self) -> responseModel.showAllDBusage:
        resp:responseModel.showAllDBusage = responseModel.showAllDBusage()
        l_DBs:list      = []
        error:str       = ""
        connected:bool  = True
        try:
            l_DBs       = await self.Mongo.list_database_names()
        except Exception as e:
            connected   = False
            error       = f'{e}'
        resp.info.connected = connected
        resp.status         = connected
        resp.info.error     = error
        resp.databaseNames  = l_DBs
        return resp

    async def collection_names_get(self) -> responseModel.showAllcollectionsUsage:
        collection:responseModel.showAllcollectionsUsage= \
                        responseModel.showAllcollectionsUsage()
        collection.collectionNames  = await self.DB.list_collection_names()
        return collection

    async def connectDB(self, DBname:str) -> dict:
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
        dbnames:responseModel.showAllDBusage = await self.database_names_get()
        d_ret:dict  = {
            'connected':        dbnames.info.connected,
            'existsAlready':    True if DBname in dbnames.databaseNames else False,
            'DB':               self.Mongo[DBname],
            'error':            dbnames.info.error
        }
        return d_ret

    def insert_one_response(self, d_resp:dict) -> dict[bool, dict]:
        d_data:dict         = {
                'status':   False,
                'document': d_resp
        }
        if 'acknowledged' in d_resp:
            d_data['status'] = d_resp['acknowledged']
        return d_data

    async def insert_one(self, collection:responseModel.collectionDesc, **kwargs) \
    -> responseModel.DocumentAddUsage:
        # pudb.set_trace()
        insert:responseModel.DocumentAddUsage   = responseModel.DocumentAddUsage()
        d_document:dict     = {}
        for k, v in kwargs.items():
            if k == 'document': d_document      = v
        insert.document     = d_document
        insert.collection   = collection
        ld_collection:list  = [d for d in self.ld_collection
                                if d['name'] == collection.name]
        for d in ld_collection:
            insert.resp     = await d['object'].document_add(d_document)
            insert.status   = insert.resp['acknowledged']
        return insert

    def collection_serialize(self) -> responseModel.collectionDesc:
        resp:responseModel.collectionDesc   = responseModel.collectionDesc()
        return resp

    async def connectCol(self, name:str) -> dict:
        colObj:mongoCollection      = mongoCollection(self)
        return {
                "name"      : name,
                "collection": await colObj.connect(name),
                "object":   colObj,
                "interface":  self.Mongo[name]
        }

    async def collection_connect(self, name:str) -> responseModel.collectionDesc:
        resp:responseModel.collectionDesc   = responseModel.collectionDesc()
        l_names     = [ x['name'] for x in self.ld_collection]
        if name not in l_names:
            self.ld_collection.append(await self.connectCol(name))
            resp    = self.ld_collection[-1]['collection']
        else:
            lookup:responseModel.collectionDesc|None = next(
                            (i['collection']
                            for i in self.ld_collection if i['name'] == name),
                            None
                      )
            if lookup: resp = lookup
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
        settingsMongo:settings.Mongo    = settings.Mongo()
        args:Namespace                  = Namespace()

        for k,v in kwargs.items():
            if k == 'settings'          : settingsMongo     = v
            if k == 'args'              : args              = v

        self.Mongo:AIO.AsyncIOMotorClient = AIO.AsyncIOMotorClient(
                                        settingsMongo.MD_URI,
                                        username    = settingsMongo.MD_username,
                                        password    = settingsMongo.MD_password
                                )
        self.ld_collection:list[dict]   = []
        self.args                       = args

    def database_serialize(self) -> responseModel.databaseDesc:
        resp:responseModel.databaseDesc = responseModel.databaseDesc()
        # pudb.set_trace()
        resp.host                       = self.DB.client.HOST
        resp.port                       = self.DB.client.PORT
        resp.name                       = str(self.DB.name)
        resp.info.connected             = self.d_DBref['connected']
        resp.info.existsAlready         = self.d_DBref['existsAlready']
        resp.info.error                 = self.d_DBref['error']
        resp.info.status                = resp.info.connected
        resp.status                     = resp.info.status
        return resp

    async def connect(self, DBname:str) -> responseModel.databaseDesc:
        self.d_DBref:dict                   = await self.connectDB(DBname)
        # pudb.set_trace()
        self.DB:AIO.AsyncIOMotorDatabase    = self.d_DBref['DB']
        return self.database_serialize()

class mongoCollection():

    async def search_on(self, d_query:dict) -> list:
        l_hits:list                     = []
        hits:AIO.AsyncIOMotorCursor     = self.collection.find(d_query)
        async for hit in hits:
            l_hits.append(hit)
        # pudb.set_trace()
        return l_hits

    def hash_addToDocument(self, d_doc:dict, l_onlyUsekeys:list = []) -> dict:
        d_newDict:dict      = copy.deepcopy(d_doc)
        d_toHash:dict       = {}
        if l_onlyUsekeys:
            d_toHash        = {k: d_doc[k] for k in l_onlyUsekeys}
        else:
            d_toHash        = d_doc
        d_sorted:dict       = dict(sorted(d_toHash.items()))
        hash                = hashlib.sha256(str(d_sorted).encode()).hexdigest()
        d_newDict['hash']   = hash
        return d_newDict

    async def is_duplicate(self, d_doc:dict) -> bool:
        b_ret:bool          = False
        if not 'hash' in d_doc.keys():
            return b_ret
        l_hits:list         = await self.search_on({
                                    'hash':     d_doc['hash']
                                })
        if len(l_hits):
            b_ret           = True
        return b_ret

    async def document_add(self, d_data:dict) -> dict:
        # pudb.set_trace()
        d_resp:dict         = {
                'acknowledged'  : False,
                'inserted_id'   : "-1",
                'error'         : ""
        }
        if self.addHashToDocument:
            d_data          = self.hash_addToDocument(d_data)
        if await self.is_duplicate(d_data) and self.noDuplicates:
           d_resp['error']  = 'Duplicate document hash found.'
        else:
            resp:results.InsertOneResult    = results.InsertOneResult(None, False)
            try:
                resp        = await self.collection.insert_one(d_data)
            except Exception as e:
                d_resp['error']     = '%s' % e
            d_resp['acknowledged']  =  resp.acknowledged
            d_resp['inserted_id']   = str(resp.inserted_id)
        return d_resp

    async def collectionNames_list(self, cursor: AIO.AsyncIOMotorCursor) -> list:
        l_collection:list   = []
        async for name in cursor:
            l_collection.append(name)
        return l_collection

    async def connectCollection(self, collection:str) -> dict:
        """
        Connect to the collection called <collection> (or create the
        collection if it does not exist). Return the collection and a
        bool exist_already/not_exist in a dictionary.

        :param mongocollection: the name of the collection
        :return: a dictionary with the collection, an element count, and
                    a status
        """
        error:str           = ""
        connected:bool      = True
        l_collection:list   = []
        try:
            l_collection    = await self.DB.list_collection_names()
        except Exception as e:
            #pudb.set_trace()
            error           = f'{e}'
            connected       = False
        d_ret:dict          = {
            'connected':    connected,
            'exists':       True if collection in l_collection else False,
            'interface':    self.DB[collection],
            'elements':     0,
            'error':        error
        }
        if d_ret['exists']:
            filter:dict       = {}
            d_ret['elements'] = await d_ret['interface'].count_documents(filter)
        return d_ret

    def __init__(self, DBobject:mongoDB) -> None:
        self.DB:AIO.AsyncIOMotorDatabase    = DBobject.getDB()
        self.d_collection:dict              = {}
        self.noDuplicates:bool              = DBobject.args.noDuplicates
        self.addHashToDocument              = DBobject.args.useHashes

    def collection_serialize(self) -> responseModel.collectionDesc:
        #pudb.set_trace()
        resp:responseModel.collectionDesc   = responseModel.collectionDesc()
        resp.databaseName                   = str(self.collection.database.name)
        resp.name                           = str(self.collection.name)
        resp.fullName                       = str(self.collection.full_name)
        resp.info.connected                 = self.d_collection['connected']
        resp.info.existsAlready             = self.d_collection['exists']
        resp.info.elements                  = self.d_collection['elements']
        resp.info.error                     = self.d_collection['error']
        resp.info.status                    = resp.info.connected
        resp.status                         = resp.info.status
        return resp

    async def connect(self, name:str) -> responseModel.collectionDesc:
        self.d_collection:dict  = await self.connectCollection(name)
        self.collection:AIO.AsyncIOMotorCollection \
                                = self.d_collection['interface']
        return self.collection_serialize()




