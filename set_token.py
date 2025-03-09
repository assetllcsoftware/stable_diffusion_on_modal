#!/usr/bin/env python
# set_token.py - Script to set up the Hugging Face token as a Modal secret

import os
import modal
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python set_token.py YOUR_HUGGING_FACE_TOKEN")
        print("Example: python set_token.py hf_abcdefghijklmnopqrstuvwxyz")
        return
    
    # Get the token from the command-line argument
    token = sys.argv[1]
    
    if not token:
        print("No token provided. Exiting.")
        return
    
    print(f"Setting up Hugging Face token (starts with {token[:4]}...) as a Modal secret")
    
    # Create the secret using the Modal CLI
    try:
        # First, check if the secret already exists and delete it if it does
        try:
            subprocess.run(["modal", "secret", "delete", "huggingface-token"], 
                          check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Deleted existing secret.")
        except Exception:
            pass
        
        # Create the new secret
        result = subprocess.run(
            ["modal", "secret", "create", "huggingface-token", f"HF_TOKEN={token}"],
            check=True, capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("Secret created successfully!")
            print("You can now deploy your application with Hugging Face authentication.")
        else:
            print(f"Error creating secret: {result.stderr}")
            
    except subprocess.CalledProcessError as e:
        print(f"Error creating secret: {e.stderr}")
        print("Make sure you have the Modal CLI installed and configured.")

if __name__ == "__main__":
    main() 