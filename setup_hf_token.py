#!/usr/bin/env python
# setup_hf_token.py - Script to set up the Hugging Face token as a Modal secret

import os
import modal
import getpass

def main():
    print("Setting up Hugging Face token as a Modal secret")
    print("You'll need to create a Hugging Face token if you don't already have one:")
    print("1. Go to https://huggingface.co/ and sign in or create an account")
    print("2. Go to your profile → Settings → Access Tokens")
    print("3. Create a new token (read access is sufficient)")
    print("4. Copy the token value")
    print()
    
    # Get the token from the user
    token = getpass.getpass("Enter your Hugging Face token: ")
    
    if not token:
        print("No token provided. Exiting.")
        return
    
    # Create the secret
    try:
        secret = modal.Secret.create(
            name="huggingface-token",
            data={"HF_TOKEN": token}
        )
        print("Secret created successfully!")
        print("You can now deploy your application with Hugging Face authentication.")
    except Exception as e:
        print(f"Error creating secret: {str(e)}")
        print("You may need to delete the existing secret first:")
        print("modal secret delete huggingface-token")

if __name__ == "__main__":
    main() 