str_description = """

    Some data models/schemas.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path

class cdResponse(BaseModel):
    path:Path       = Path("")
    message:str     = ""
    status:bool     = True
    error:str       = ""
    code:int        = 0
    state:dict      = {
                        "database":     "",
                        "collection":   ""
                       }


