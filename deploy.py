#!/usr/bin/env python
# deploy.py - Script to deploy the application to Modal

import subprocess
import sys

if __name__ == "__main__":
    # Deploy the application to Modal
    print("Deploying Stable Diffusion XL (Illustrious) to Modal...")
    
    # Use the modal CLI to deploy the app.py file
    result = subprocess.run(["modal", "deploy", "app.py", "--name", "stable-diffusion-app"], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Deployment complete!")
        print("Your application is now available at the Modal URL.")
        print("You can find the URL in the Modal dashboard.")
        print("Visit https://modal.com/apps to view your deployed applications.")
        print("\nOutput from deployment:")
        print(result.stdout)
        print("\nNotes:")
        print("1. The first time you generate an image may take longer as the Illustrious XL model is loaded.")
        print("2. If the local checkpoint isn't found, the app will fall back to the base SDXL from Hugging Face.")
    else:
        print("Deployment failed!")
        print("Error message:")
        print(result.stderr)
        sys.exit(1) 