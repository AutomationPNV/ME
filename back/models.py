from pydantic import BaseModel

class AddMotor(BaseModel):
    name_motor: str
    ip_tesys: str
    ip_plc: str
    location: str
