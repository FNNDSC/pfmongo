import  os
from    pydantic_settings   import BaseSettings
from    pfmongo.models      import dataModel
from    typing              import Optional

class Mongo(BaseSettings):
    MD_URI:str          = "localhost:27017"
    MD_DB:str           = ""
    MD_COLLECTION:str   = ""
    MD_username:str     = "username"
    MD_password:str     = "password"
    MD_sessionUser:str  = ""
    stateDBname:str     = "db.txt"
    stateColname:str    = "collection.txt"

class App(BaseSettings):
    logging:dataModel.loggingType = dataModel.loggingType.CONSOLE


logging_val:Optional[str] = 'CONSOLE'
if 'LOGGING' in os.environ:
    logging_val         = os.environ['LOGGING']
logging_enum:dataModel.loggingType  = dataModel.loggingType.CONSOLE
if logging_val:
    try:
        logging_enum    = dataModel.loggingType[logging_val]
    except KeyError:
        logging_enum    = dataModel.loggingType.CONSOLE

mongosettings   = Mongo()
appsettings     = App(logging = logging_enum)
