from typing import Optional
from pydantic import BaseModel
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from config import Base


class MsgPayload(BaseModel):
    msg_id: Optional[int]
    msg_name: str

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    geometry = Column(Geometry('POINT'))
