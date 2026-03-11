from   pydantic import BaseModel

class Motor(BaseModel):
    id: int
    name_motors: str
    ip_tesys: str
    ip_plc: str
    location: str
