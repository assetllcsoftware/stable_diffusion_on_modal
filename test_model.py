#!/usr/bin/env python
# test_model.py - Test script for the Stable Diffusion model

import os
import argparse
from stable_diffusion import StableDiffusionModel
from utils.helpers import ensure_directory

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Stable Diffusion model")
    parser.add_argument("--prompt", type=str, default="A beautiful sunset over a mountain landscape, digital art", help="The prompt to generate an image from")
    parser.add_argument("--output", type=str, default="test_output.png", help="The path to save the generated image to")
    parser.add_argument("--width", type=int, default=512, help="The width of the generated image")
    parser.add_argument("--height", type=int, default=512, help="The height of the generated image")
    parser.add_argument("--steps", type=int, default=50, help="Number of denoising steps")
    parser.add_argument("--guidance", type=float, default=7.5, help="Guidance scale for the diffusion process")
    args = parser.parse_args()
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        ensure_directory(output_dir)
    
    # Initialize the model
    print("Initializing Stable Diffusion model...")
    model = StableDiffusionModel()
    
    # Generate the image
    print(f"Generating image with prompt: '{args.prompt}'")
    print(f"This may take a minute or two...")
    
    try:
        # Call the Modal function to generate the image
        model.generate_image.remote(
            prompt=args.prompt,
            output_path=args.output,
            width=args.width,
            height=args.height,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance
        )
        
        print(f"Image generated successfully and saved to: {args.output}")
    except Exception as e:
        print(f"Error generating image: {e}")

if __name__ == "__main__":
    main() 