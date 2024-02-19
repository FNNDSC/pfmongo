import  os
from    pydantic_settings   import BaseSettings
from    pfmongo.models      import dataModel
from    typing              import Optional

class Mongo(BaseSettings):
    MD_URI:str              = "localhost:27017"
    MD_DB:str               = ""
    MD_COLLECTION:str       = ""
    MD_username:str         = "username"
    MD_password:str         = "password"
    MD_sessionUser:str      = ""
    stateDBname:str         = "db.txt"
    stateColname:str        = "collection.txt"
    stateDupname:str        = "duplicates.txt"
    stateHashes:str         = "hashes.txt"
    flattenSuffix:str       = "-flat"
    responseTruncDepth:int  = 4
    responseTruncSize:int   = 6000
    responseTruncOver:int   = 100000

class App(BaseSettings):
    logging:dataModel.loggingType = dataModel.loggingType.CONSOLE
    allowDuplicates:bool    = True
    noHashing:bool          = True
    donotFlatten:bool       = False
    beQuiet:bool            = False
    noResponseTruncSize:bool= True
    noComplain:bool         = False
    detailedOutput:bool     = False
    modelSizesPrint:bool    = False
    eventLoopDebug:bool     = False
    fontawesomeUse:bool     = True

logging_val:Optional[str]   = 'CONSOLE'
if 'LOGGING' in os.environ:
    logging_val             = os.environ['LOGGING']
logging_enum:dataModel.loggingType  = dataModel.loggingType.CONSOLE
if logging_val:
    try:
        logging_enum        = dataModel.loggingType[logging_val]
    except KeyError:
        logging_enum        = dataModel.loggingType.CONSOLE

mongosettings:Mongo         = Mongo()
appsettings:App             = App(logging = logging_enum)
