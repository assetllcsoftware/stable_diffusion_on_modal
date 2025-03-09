#!/usr/bin/env python
# simple_upload.py - A simplified script to upload a model file to a Modal volume

import os
import modal
import time
import shutil

# Create a Modal app
app = modal.App("simple-uploader")

# Create a volume
volume = modal.Volume.from_name("stable-diffusion-models", create_if_missing=True)

# Create a simple image
image = modal.Image.debian_slim()

# Define the model file path
MODEL_FILE = "stableDiffusion35_medium.safetensors"

# Add the model file to the image
image = image.add_local_file(MODEL_FILE, "/model.safetensors")

@app.function(
    image=image,
    volumes={"/vol": volume},
    timeout=3600,  # 1 hour timeout for large file upload
)
def upload_file():
    """Upload a file to the Modal volume."""
    import os
    import shutil
    import time
    
    # Print current directory contents
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    
    # Check if the model file exists in the container
    model_path = "/model.safetensors"
    if os.path.exists(model_path):
        print(f"Model file found at {model_path}")
        print(f"File size: {os.path.getsize(model_path) / (1024 * 1024 * 1024):.2f} GB")
        
        # Create the destination directory if it doesn't exist
        os.makedirs("/vol", exist_ok=True)
        
        # Define the destination path
        dest_path = "/vol/stableDiffusion35_medium.safetensors"
        
        # Check if the file already exists in the volume
        if os.path.exists(dest_path):
            print(f"Model file already exists at {dest_path}")
            print(f"File size: {os.path.getsize(dest_path) / (1024 * 1024 * 1024):.2f} GB")
            return dest_path
        
        # Start timing
        start_time = time.time()
        
        # Copy the file to the volume
        print(f"Copying model file to volume at {dest_path}...")
        shutil.copy(model_path, dest_path)
        
        # End timing
        end_time = time.time()
        
        # Check if the file was copied successfully
        if os.path.exists(dest_path):
            file_size_gb = os.path.getsize(dest_path) / (1024 * 1024 * 1024)
            print(f"Model file copied successfully to {dest_path}")
            print(f"File size: {file_size_gb:.2f} GB")
            print(f"Copy took {end_time - start_time:.2f} seconds")
            
            # List all files in the volume
            print("\nAll files in the volume:")
            for file in os.listdir("/vol"):
                file_path = os.path.join("/vol", file)
                if os.path.isfile(file_path):
                    size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
                    print(f"- {file} ({size_gb:.2f} GB)")
                else:
                    print(f"- {file} (directory)")
            
            return dest_path
        else:
            print(f"Failed to copy model file to {dest_path}")
            return None
    else:
        print(f"Model file not found at {model_path}")
        print(f"Current directory contents: {os.listdir('/')}")
        return None

@app.local_entrypoint()
def main():
    print("Starting upload process...")
    result = upload_file.remote()
    print(f"Result: {result}")
    print("Upload process completed.") 