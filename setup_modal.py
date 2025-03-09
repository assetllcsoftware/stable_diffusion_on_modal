#!/usr/bin/env python
# setup_modal.py - Script to set up the Modal environment

import os
import subprocess
import sys

def main():
    print("Setting up the Modal environment...")
    
    # Check if Modal is installed
    try:
        import modal
        print("Modal is already installed.")
    except ImportError:
        print("Modal is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "modal"])
    
    # Check if the Modal token is set up
    if not os.path.exists(os.path.expanduser("~/.modal/config.json")):
        print("Modal token is not set up. Please run 'modal token new' to set it up.")
        print("You will need to create a Modal account at https://modal.com if you don't have one.")
        subprocess.call(["modal", "token", "new"])
    else:
        print("Modal token is already set up.")
    
    print("\nModal environment setup complete!")
    print("\nNext steps:")
    print("1. Run 'python test_model.py' to test the Stable Diffusion model")
    print("2. Run 'python run_app.py' to start the web application")

if __name__ == "__main__":
    main() 