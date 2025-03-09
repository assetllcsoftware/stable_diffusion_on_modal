#!/usr/bin/env python
# run_app.py - Script to run the web application

import os
import uvicorn
from app import fastapi_app
from utils.helpers import ensure_directory

def main():
    # Ensure the images directory exists
    ensure_directory("images")
    
    # Ensure the web/static directory exists
    ensure_directory("web/static")
    
    # Run the application
    print("Starting the Stable Diffusion web application...")
    print("Open http://localhost:8000 in your browser to access the application")
    
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 