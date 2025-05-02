"""
FastAPI Main Application Module

This module defines the FastAPI application and its endpoints for managing
geographic locations. It provides RESTful API endpoints for creating,
reading, and deleting location data with PostGIS integration.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Location
from config import SessionLocal, engine, Base
from pydantic import BaseModel
from geoalchemy2.shape import to_shape
import random
import osmnx as ox
import numpy as np
from shapely.geometry import Point, Polygon
from itertools import combinations

app = FastAPI(
    title="GeoPoint FastAPI Service",
    description="A geospatial microservice for managing location data",
    version="1.0.0"
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    """
    Dependency that provides a database session for each request.
    Ensures proper closing of the session after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LocationCreate(BaseModel):
    """
    Pydantic model for location creation requests.
    Validates incoming data for new location entries.
    """
    name: str
    description: str
    latitude: float
    longitude: float

class LocationResponse(BaseModel):
    """
    Pydantic model for location responses.
    Defines the structure of location data sent back to clients.
    """
    id: int
    name: str
    description: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastAPI Geo Service"}

@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}

@app.post("/locations/", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = Location(
        name=location.name,
        description=location.description,
        geometry=f'POINT({location.longitude} {location.latitude})'
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    # Extract coordinates from geometry
    point = to_shape(db_location.geometry)
    return {
        "id": db_location.id,
        "name": db_location.name,
        "description": db_location.description,
        "latitude": point.y,
        "longitude": point.x
    }

@app.get("/locations/", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    response_locations = []
    for loc in locations:
        point = to_shape(loc.geometry)
        response_locations.append({
            "id": loc.id,
            "name": loc.name,
            "description": loc.description,
            "latitude": point.y,
            "longitude": point.x
        })
    return response_locations

@app.delete("/locations/all")
def delete_all_locations(db: Session = Depends(get_db)):
    """
    Deletes all locations from the database.
    Returns the count of deleted locations.
    """
    try:
        # Get count before deletion
        count = db.query(Location).count()
        
        # Delete all locations
        db.query(Location).delete()
        db.commit()
        
        return {
            "message": f"Successfully deleted {count} locations",
            "count": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete locations: {str(e)}"
        )

@app.delete("/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    db.delete(location)
    db.commit()
    return {"message": f"Location {location_id} deleted"}

# Constants for continental US boundaries
US_BOUNDS = {
    "north": 49.3457868,  # Washington state
    "south": 24.396308,   # Florida
    "east": -66.945392,   # Maine
    "west": -124.848974,  # California
}

@app.post("/locations/create-road-square", response_model=List[LocationResponse])
def create_road_square_locations(db: Session = Depends(get_db)):
    """
    Creates 4 location points at road intersections forming an approximate square
    within the continental US. Retries with different locations if no roads found.
    """
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Generate random center point
            center_lat = random.uniform(US_BOUNDS["south"], US_BOUNDS["north"])
            center_lon = random.uniform(US_BOUNDS["west"], US_BOUNDS["east"])
            
            # Get road network around random point with larger radius
            G = ox.graph_from_point(
                (center_lat, center_lon),
                dist=1000,  # 1km radius (increased from 500m)
                network_type='drive',
                simplify=True
            )
            
            # Get node coordinates
            nodes = ox.graph_to_gdfs(G, edges=False)
            
            if len(nodes) < 4:
                continue  # Try again if not enough nodes
            
            # Get all node coordinates
            coords = np.array([[node['y'], node['x']] for _, node in nodes.iterrows()])
            
            # Find nodes that form the most square-like shape
            best_square = None
            best_score = float('inf')
            
            # Try different combinations of 4 nodes (limit to 1000 combinations)
            for points in list(combinations(coords, 4))[:1000]:
                poly = Polygon(points)
                
                # Calculate how "square-like" the shape is
                min_x, min_y, max_x, max_y = poly.bounds
                width = max_x - min_x
                height = max_y - min_y
                
                # Score based on aspect ratio and size
                aspect_score = abs(1 - (width/height))
                size_score = abs(1 - ((width * height) / (0.5 * 0.5)))  # aim for ~0.5km square
                score = aspect_score + size_score
                
                if score < best_score:
                    best_score = score
                    best_square = points
            
            if best_square is not None:
                # Create locations from best square corners
                created_locations = []
                for i, point in enumerate(best_square):
                    corner = ['NE', 'SE', 'SW', 'NW'][i]
                    db_location = Location(
                        name=f"Road Square {corner} ({point[0]:.4f}, {point[1]:.4f})",
                        description=f"{corner} corner of road-based square near {center_lat:.4f}, {center_lon:.4f}",
                        geometry=f'POINT({point[1]} {point[0]})'
                    )
                    db.add(db_location)
                    db.commit()
                    db.refresh(db_location)
                    
                    # Extract coordinates
                    geom_point = to_shape(db_location.geometry)
                    created_locations.append({
                        "id": db_location.id,
                        "name": db_location.name,
                        "description": db_location.description,
                        "latitude": geom_point.y,
                        "longitude": geom_point.x
                    })
                
                return created_locations
                
        except Exception as e:
            if attempt == max_attempts - 1:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to find suitable road network after {max_attempts} attempts"
                )
            continue
    
    raise HTTPException(
        status_code=500,
        detail="Could not find suitable road network"
    )
