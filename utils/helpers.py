#!/usr/bin/env python
# helpers.py - Utility functions for the Stable Diffusion application

import os
import base64
from io import BytesIO
from PIL import Image
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directory(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: The path to the directory to ensure exists
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")

def image_to_base64(image_path):
    """
    Convert an image to a base64 string.
    
    Args:
        image_path: The path to the image to convert
    
    Returns:
        A base64 string representation of the image
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        return None

def base64_to_image(base64_string, output_path):
    """
    Convert a base64 string to an image and save it.
    
    Args:
        base64_string: The base64 string to convert
        output_path: The path to save the image to
    
    Returns:
        The path to the saved image
    """
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error converting base64 to image: {e}")
        return None

def get_timestamp():
    """
    Get a formatted timestamp.
    
    Returns:
        A formatted timestamp string
    """
    return time.strftime("%Y%m%d-%H%M%S")

def clean_prompt(prompt):
    """
    Clean a prompt string for use in filenames.
    
    Args:
        prompt: The prompt to clean
    
    Returns:
        A cleaned prompt string
    """
    # Replace special characters with underscores
    cleaned = ''.join(c if c.isalnum() else '_' for c in prompt)
    # Truncate to a reasonable length
    return cleaned[:50]

def generate_filename(prompt):
    """
    Generate a filename for a generated image.
    
    Args:
        prompt: The prompt used to generate the image
    
    Returns:
        A filename for the generated image
    """
    timestamp = get_timestamp()
    cleaned_prompt = clean_prompt(prompt)
    return f"{timestamp}_{cleaned_prompt}.png" 