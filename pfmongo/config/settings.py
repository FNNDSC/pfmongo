import  os
from    pydantic_settings   import BaseSettings

class Mongo(BaseSettings):
    MD_URI:str          = "localhost:27017"
    MD_DB:str           = ""
    MD_username:str     = "username"
    MD_password:str     = "password"
    MD_sessionUser:str  = ""
    stateDBname:str     = "db.txt"
    stateColname:str    = "collection.txt"

mongosettings   = Mongo()
