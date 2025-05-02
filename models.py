"""
Database Models Module

This module defines the SQLAlchemy models for the application.
It includes the Location model which uses PostGIS for spatial data storage.
"""

from typing import Optional
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from config import Base

class Location(Base):
    """
    SQLAlchemy model representing a geographic location in the database.
    Uses PostGIS geometry type for storing spatial data.
    
    Table: locations
    
    Attributes:
        id (int): Primary key for the location
        name (str): Name of the location
        description (str): Detailed description of the location
        geometry (Geometry): PostGIS POINT geometry storing latitude and longitude
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    # SRID 4326 corresponds to WGS84 coordinate system (standard for GPS)
    geometry = Column(Geometry('POINT', srid=4326))
