# GeoPoint FastAPI Service

A modern geospatial microservice built with FastAPI and PostGIS, featuring interactive map visualization.

## Features

- RESTful API for location management
- PostgreSQL with PostGIS spatial database
- Interactive map visualization using Folium
- Marker clustering for better data representation
- SQLAlchemy ORM with GeoAlchemy2 integration

## Tech Stack

- FastAPI
- PostgreSQL + PostGIS
- SQLAlchemy + GeoAlchemy2
- Folium
- Jupyter Notebook

## Quick Start

1. Set up the database:
```sql
CREATE DATABASE geodatabase;
\c geodatabase
CREATE EXTENSION postgis;
```

2. Install dependencies:
```bash
pip install "fastapi[all]" sqlalchemy geoalchemy2 psycopg2-binary folium pandas jupyter
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the service:
```bash
uvicorn main:app --reload
```

5. View the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

6. Launch the map viewer:
```bash
jupyter notebook map_viewer.ipynb
```

## API Endpoints

- `GET /locations/` - List all locations
- `POST /locations/` - Create a new location
- `DELETE /locations/{location_id}` - Delete a location

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT

## Author

[Your Name]
