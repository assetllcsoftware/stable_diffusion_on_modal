#!/usr/bin/env python
# check_token.py - Script to check if the Hugging Face token is set up correctly

import os
import modal
import sys
import subprocess

def main():
    print("Checking if Hugging Face token is set up correctly...")
    
    # First, check if the secret exists using the Modal CLI
    try:
        result = subprocess.run(
            ["modal", "secret", "list"],
            check=True, capture_output=True, text=True
        )
        
        if "huggingface-token" in result.stdout:
            print("✅ Hugging Face token secret exists in Modal")
        else:
            print("❌ Hugging Face token secret does not exist in Modal")
            print("Run 'python set_token.py YOUR_HUGGING_FACE_TOKEN' to set it up.")
            return
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking secrets: {e.stderr}")
        print("Make sure you have the Modal CLI installed and configured.")
        return
    
    # Now test if the secret works in a Modal function
    try:
        # Create a simple app to test the secret
        app = modal.App("token-checker")
        
        @app.function(secrets=[modal.Secret.from_name("huggingface-token")])
        def check_token():
            token = os.environ.get("HF_TOKEN", "")
            if token:
                masked_token = token[:4] + "..." + token[-4:] if len(token) > 8 else "***"
                return f"✅ Token is available in the environment: {masked_token}"
            else:
                return "❌ Token is not available in the environment"
        
        result = check_token.remote()
        print(result)
        
    except Exception as e:
        print(f"❌ Error testing token: {str(e)}")
        print("The Hugging Face token secret may exist but there was an error accessing it.")

if __name__ == "__main__":
    main() 