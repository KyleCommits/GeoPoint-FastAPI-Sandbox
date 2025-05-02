"""
Database Configuration Module

This module handles the PostgreSQL database connection setup using SQLAlchemy.
It loads environment variables for secure credential management and creates
the database engine and session maker.

Environment Variables Required:
    DB_USER: PostgreSQL username
    DB_PASSWORD: PostgreSQL password
    DB_HOST: Database host (typically 'localhost')
    DB_PORT: Database port (typically '5432')
    DB_NAME: Name of the geodatabase
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Construct database URL using environment variables
SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create SQLAlchemy engine for database connections
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create sessionmaker for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for SQLAlchemy models
Base = declarative_base()