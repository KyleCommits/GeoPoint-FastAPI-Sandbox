from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Location
from config import SessionLocal, engine, Base
from pydantic import BaseModel
from geoalchemy2.shape import to_shape

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LocationCreate(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float

class LocationResponse(BaseModel):
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

@app.delete("/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    db.delete(location)
    db.commit()
    return {"message": f"Location {location_id} deleted"}
