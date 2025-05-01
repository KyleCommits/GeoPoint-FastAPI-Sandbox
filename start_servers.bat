@echo off
start cmd /k "uvicorn main:app --reload"
start cmd /k "jupyter notebook map_viewer.ipynb"
start http://localhost:8000/docs
start http://localhost:8888/notebooks/map_viewer.ipynb