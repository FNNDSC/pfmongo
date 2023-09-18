from    argparse            import Namespace
from    typing              import Any, List, TypedDict
from    pydantic            import BaseModel, Field

import  json
from    datetime            import datetime
from    pathlib             import Path

try:
    from    config              import settings
except:
    from    ..config             import settings
import  sys
import  shutil
import  pudb

import  pymongo
from    pymongo             import MongoClient
from    pymongo.database    import Database
from    pymongo.collection  import Collection
from    pymongo             import results

from    motor               import motor_asyncio as AIO

import  hashlib
import  copy

class mongoDB():

    def getDB(self) -> AIO.AsyncIOMotorDatabase:
        return self.DB

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
        l_DBs:list  = await self.Mongo.list_database_names()
        d_ret:dict  = {
            'existsAlready':    True if DBname in l_DBs else False,
            'DB':               self.Mongo[DBname]
        }
        return d_ret

    def insert_one_response(self, d_resp:dict) -> dict:
        d_data:dict         = {
                'status':   False,
                'document': d_resp
        }
        if 'acknowledged' in d_resp:
            d_data['status'] = d_resp['acknowledged']
        return d_data

    async def insert_one(self, **kwargs) -> dict[bool, dict]:
        d_document:dict     = {}
        d_data:dict         = {
                'status':   False,
                'document': d_document
        }
        d_document          = {}
        intoCollection:str  = ""
        for k, v in kwargs.items():
            if k == 'intoCollection':   intoCollection  = v
            if k == 'document':         d_document      = v
        if not intoCollection:
            return d_data
        await self.collection_add(intoCollection)
        ld_collection:list = [d for d in self.ld_collection
                                if d['name'] == intoCollection]
        for d in ld_collection:
            d_data          = self.insert_one_response(
                                await d['collection'].document_add(d_document)
                            )
        return d_data

    async def collection_add(self, name:str) -> bool:
        b_ret:bool  = False
        l_names     = [ x['name'] for x in self.ld_collection]
        if name not in l_names:
            b_ret                   = True
            colObj:mongoCollection  = mongoCollection(self)
            self.ld_collection.append({
                "name"      : name,
                "collection": colObj
            })
            await colObj.connect(name)
        return b_ret

    def __init__(self, **kwargs) -> None:
        """
        The constructor for the mongo data base "object". Each "object"
        is connected to a single mongo database, which can contain a variable
        number of collections (described in a list).

        For "simplicity sake" in this formulation, create a separate object
        for each DB in Mongo.

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

    async def connect(self, DBname:str) -> None:
        self.d_DBref:dict                   = await self.connectDB(DBname)
        self.DB:AIO.AsyncIOMotorDatabase    = self.d_DBref['DB']

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
                'acknowledged': False,
                'inserted_id':  "-1"
        }
        if self.hash_addToDocument:
            d_data          = self.hash_addToDocument(d_data)
        if await self.is_duplicate(d_data) and self.noDuplicates:
           d_resp['error']  = 'Duplicate document hash found.'
        else:
            resp:results.InsertOneResult = await self.collection.insert_one(d_data)
            d_resp = {
                'acknowledged': resp.acknowledged,
                'inserted_id':  str(resp.inserted_id)
            }
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

        l_collection:list   = await self.DB.list_collection_names()
        d_ret:dict          = {
            'exists':       True if collection in l_collection else False,
            'interface':    self.DB[collection],
            'elements':     0
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

    async def connect(self, name:str) -> None:
        self.d_collection:dict  = await self.connectCollection(name)
        self.collection:AIO.AsyncIOMotorCollection \
                                = self.d_collection['interface']


