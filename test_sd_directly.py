#!/usr/bin/env python
# test_sd_directly.py - Test the Stable Diffusion model directly

import os
import modal
import time

# Create a simple image
image = modal.Image.debian_slim().pip_install(
    "diffusers==0.14.0",
    "transformers==4.25.1",
    "accelerate==0.16.0",
    "torch==2.0.0",
    "pillow==9.3.0",
)

# Create a Modal app
app = modal.App("sd-test")

@app.function(image=image, gpu="T4", timeout=600)
def generate_image(prompt: str, output_path: str = "test_output.png"):
    """Generate an image using Stable Diffusion."""
    import torch
    from diffusers import StableDiffusionPipeline
    
    print(f"Generating image for prompt: {prompt}")
    print(f"Output path: {output_path}")
    
    # Start timing
    start_time = time.time()
    
    try:
        # Initialize the pipeline
        print("Initializing StableDiffusionPipeline...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
        )
        print("Moving pipeline to CUDA...")
        pipe = pipe.to("cuda")
        
        # Generate the image
        print("Generating image...")
        image = pipe(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=50,
            guidance_scale=7.5,
        ).images[0]
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Save the image
        print(f"Saving image to: {output_path}")
        image.save(output_path)
        
        # Print the time taken
        end_time = time.time()
        print(f"Image generated in {end_time - start_time:.2f} seconds")
        
        return "Success"
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

@app.local_entrypoint()
def main():
    prompt = "A beautiful sunset over mountains, digital art style"
    result = generate_image.remote(prompt)
    print(f"Result: {result}")
    print("Check the test_output.png file for the generated image.") 