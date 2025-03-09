#!/usr/bin/env python
# upload_model.py - Script to upload the Stable Diffusion model to a Modal volume

import os
import modal
import time
import sys

print("Script started")
print(f"Current directory: {os.getcwd()}")

# Path to the model file
MODEL_PATH = "stableDiffusion35_medium.safetensors"
ABSOLUTE_MODEL_PATH = os.path.abspath(MODEL_PATH)

# Check if the file exists locally
if not os.path.exists(ABSOLUTE_MODEL_PATH):
    print(f"Error: Model file not found at {ABSOLUTE_MODEL_PATH}")
    sys.exit(1)

print(f"Model file exists, size: {os.path.getsize(ABSOLUTE_MODEL_PATH) / (1024 * 1024 * 1024):.2f} GB")

# Create a Modal volume for storing the model
print("Creating Modal volume...")
model_volume = modal.Volume.from_name("stable-diffusion-models", create_if_missing=True)
print("Modal volume created")

# Create a Modal app
app = modal.App("model-uploader")

# Create a base image
image = modal.Image.debian_slim()

# Add the model file to the image
image = image.add_local_file(ABSOLUTE_MODEL_PATH, "/model.safetensors")

@app.function(image=image, volumes={"/models": model_volume})
def upload_model():
    """Upload the model file to the Modal volume."""
    import os
    import shutil
    import time
    
    print("Inside upload_model function")
    
    # Source path (mounted file)
    src_path = "/model.safetensors"
    
    # Create the destination directory if it doesn't exist
    os.makedirs("/models", exist_ok=True)
    print("Created /models directory")
    
    # Define the destination path
    dest_path = f"/models/{os.path.basename(MODEL_PATH)}"
    print(f"Destination path: {dest_path}")
    
    # Check if the file already exists in the volume
    if os.path.exists(dest_path):
        print(f"Model file already exists at {dest_path}")
        print(f"File size: {os.path.getsize(dest_path) / (1024 * 1024 * 1024):.2f} GB")
        return dest_path
    
    # Start timing
    start_time = time.time()
    
    # Copy the file to the volume
    print(f"Uploading model to Modal volume...")
    print(f"Source path: {src_path}, size: {os.path.getsize(src_path) / (1024 * 1024 * 1024):.2f} GB")
    shutil.copy(src_path, dest_path)
    
    # End timing
    end_time = time.time()
    
    # Check if the file was uploaded successfully
    if os.path.exists(dest_path):
        file_size_gb = os.path.getsize(dest_path) / (1024 * 1024 * 1024)
        print(f"Model uploaded successfully to {dest_path}")
        print(f"File size: {file_size_gb:.2f} GB")
        print(f"Upload took {end_time - start_time:.2f} seconds")
        
        # List all files in the volume
        print("\nAll files in the volume:")
        for file in os.listdir("/models"):
            file_path = os.path.join("/models", file)
            size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
            print(f"- {file} ({size_gb:.2f} GB)")
        
        return dest_path
    else:
        print(f"Failed to upload model to {dest_path}")
        return None

@app.local_entrypoint()
def main():
    print("Running upload_model...")
    result = upload_model.remote()
    print(f"Result: {result}")
    print("Model upload process completed") 