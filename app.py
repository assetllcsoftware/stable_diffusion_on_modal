#!/usr/bin/env python
# app.py - Main application entry point

import os
import modal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import Optional
import io
import base64

# Get Hugging Face token from environment variable (will be set during deployment)
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Create a Modal image with all required dependencies
image = modal.Image.debian_slim().pip_install(
    "diffusers>=0.26.3",
    "transformers>=4.36.2",
    "accelerate>=0.27.2",
    "torch>=2.2.0",
    "pillow>=10.1.0",
    "fastapi>=0.109.0",
    "python-dotenv>=1.0.0",
    "safetensors>=0.4.1",
    "huggingface-hub>=0.19.0",
    "sentencepiece>=0.1.99",
)

# Add local Python modules to the image
image = image.add_local_python_source("utils")
image = image.add_local_python_source("app")

# Create a Modal app
app = modal.App("stable-diffusion-app")

# Create a volume for storing generated images
volume = modal.Volume.from_name("stable-diffusion-images", create_if_missing=True)
VOLUME_PATH = "/images"

# Create a FastAPI app
fastapi_app = FastAPI(title="Stable Diffusion API")

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to get the Hugging Face token secret
try:
    hf_secret = modal.Secret.from_name("huggingface-token")
    print("Successfully loaded Hugging Face token secret")
except Exception as e:
    print(f"Warning: Could not load Hugging Face token secret: {str(e)}")
    print("The application will still work, but may not be able to access gated models.")
    hf_secret = None

# Create directories
@app.function(
    image=image, 
    volumes={VOLUME_PATH: volume},
    secrets=[hf_secret] if hf_secret is not None else []
)
def create_directories():
    # Create a directory for storing generated images
    os.makedirs(VOLUME_PATH, exist_ok=True)
    # List the contents of the volume
    contents = os.listdir(VOLUME_PATH)
    print(f"Contents of {VOLUME_PATH} after creating directory: {contents}")
    
    return "Directories created"

# Define the Stable Diffusion model class
@app.cls(
    image=image, 
    gpu="A10G", 
    timeout=900, 
    volumes={VOLUME_PATH: volume},
    secrets=[hf_secret] if hf_secret is not None else []
)
class StableDiffusionModel:
    def __init__(self):
        self.model_id = "stabilityai/stable-diffusion-3.5-medium"
        print(f"StableDiffusionModel initialized with model_id: {self.model_id}")
        
        # Set Hugging Face token in environment if available
        if "HF_TOKEN" in os.environ and os.environ["HF_TOKEN"]:
            print("Hugging Face token found in environment")
            # Set the token for the Hugging Face Hub library
            os.environ["HUGGING_FACE_HUB_TOKEN"] = os.environ["HF_TOKEN"]
        else:
            print("WARNING: No Hugging Face token found in environment")
        
        # Ensure the images directory exists
        os.makedirs(VOLUME_PATH, exist_ok=True)
        print(f"Contents of {VOLUME_PATH} in StableDiffusionModel.__init__: {os.listdir(VOLUME_PATH)}")
    
    @modal.method()
    def generate_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 30,
        guidance_scale: float = 8.0,
        negative_prompt: Optional[str] = None,
    ):
        """
        Generate an image from a text prompt using Stable Diffusion 3.5.
        
        Args:
            prompt: The text prompt to generate an image from
            output_path: The path to save the generated image to
            width: The width of the generated image
            height: The height of the generated image
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for the diffusion process
            negative_prompt: Optional negative prompt for the generation
        
        Returns:
            The path to the generated image and the base64-encoded image data
        """
        try:
            import torch
            from diffusers import DiffusionPipeline, AutoencoderKL
            from PIL import Image
            import huggingface_hub
            
            # Print some information
            print(f"Generating image for prompt: {prompt}")
            print(f"Output path: {output_path}")
            print(f"Width: {width}, Height: {height}")
            print(f"Steps: {num_inference_steps}, Guidance scale: {guidance_scale}")
            
            # Check if we have a Hugging Face token
            if "HUGGING_FACE_HUB_TOKEN" in os.environ and os.environ["HUGGING_FACE_HUB_TOKEN"]:
                print("Using Hugging Face token for authentication")
                huggingface_hub.login(token=os.environ["HUGGING_FACE_HUB_TOKEN"])
            
            # Start timing
            start_time = time.time()
            
            # Initialize the pipeline directly from Hugging Face
            print(f"Initializing DiffusionPipeline from Hugging Face: {self.model_id}")
            pipe = DiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
            )
            
            print("Moving pipeline to CUDA...")
            pipe = pipe.to("cuda")
            
            # Generate the image
            print("Generating image with SD 3.5...")
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
            ).images[0]
            
            # Create the output directory if it doesn't exist
            print(f"Creating output directory: {os.path.dirname(output_path)}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the image
            print(f"Saving image to: {output_path}")
            image.save(output_path)
            
            # Check if the file was saved
            if os.path.exists(output_path):
                print(f"Image file exists at {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")
            else:
                print(f"WARNING: Image file does not exist at {output_path}")
            
            # List the contents of the volume
            contents = os.listdir(VOLUME_PATH)
            print(f"Contents of {VOLUME_PATH} after saving image: {contents}")
            
            # Convert the image to base64 for direct embedding
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Print the time taken
            end_time = time.time()
            print(f"Image generated in {end_time - start_time:.2f} seconds")
            
            return {"path": output_path, "base64_image": img_str}
        except Exception as e:
            print(f"Error in generate_image: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

# Initialize the Stable Diffusion model
sd_model = StableDiffusionModel()

@fastapi_app.get("/", response_class=HTMLResponse)
async def read_root():
    # Return the HTML content directly
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stable Diffusion Image Generator</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>Stable Diffusion Image Generator</h1>
            <p>Generate images from text prompts using Stable Diffusion</p>
        </header>
        
        <main>
            <div class="form-container">
                <form id="generation-form">
                    <div class="form-group">
                        <label for="prompt">Text Prompt</label>
                        <textarea id="prompt" name="prompt" rows="3" placeholder="Enter a detailed description of the image you want to generate..." required></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="width">Width</label>
                            <input type="number" id="width" name="width" value="1024" min="256" max="1024" step="64">
                        </div>
                        
                        <div class="form-group">
                            <label for="height">Height</label>
                            <input type="number" id="height" name="height" value="1024" min="256" max="1024" step="64">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="steps">Steps</label>
                            <input type="number" id="steps" name="num_inference_steps" value="30" min="10" max="150">
                        </div>
                        
                        <div class="form-group">
                            <label for="guidance">Guidance Scale</label>
                            <input type="number" id="guidance" name="guidance_scale" value="8.0" min="1" max="20" step="0.5">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <button type="submit" id="generate-btn">Generate Image</button>
                    </div>
                </form>
            </div>
            
            <div class="result-container">
                <div id="loading" class="hidden">
                    <div class="spinner"></div>
                    <p>Generating image... This may take a minute.</p>
                </div>
                
                <div id="result" class="hidden">
                    <h2>Generated Image</h2>
                    <div class="image-container">
                        <img id="generated-image" src="" alt="Generated image">
                    </div>
                    <div class="actions">
                        <button id="download-btn">Download Image</button>
                        <button id="new-generation-btn">New Generation</button>
                    </div>
                </div>
                
                <div id="error" class="hidden">
                    <p>An error occurred while generating the image:</p>
                    <p id="error-message" class="error-details">Please try again.</p>
                </div>
            </div>
        </main>
        
        <footer>
            <p>Powered by Modal and Stable Diffusion</p>
        </footer>
    </div>
    
    <script src="/static/js/script.js"></script>
</body>
</html>
    """

@fastapi_app.get("/static/css/style.css")
async def get_css():
    return Response(content="""
/* style.css - Styles for the Stable Diffusion web interface */

:root {
    --primary-color: #6200ee;
    --primary-dark: #3700b3;
    --secondary-color: #03dac6;
    --background-color: #f5f5f5;
    --surface-color: #ffffff;
    --error-color: #b00020;
    --text-primary: #333333;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
    --shadow-color: rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    margin-bottom: 2rem;
}

header h1 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

main {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

@media (min-width: 768px) {
    main {
        grid-template-columns: 1fr 1fr;
    }
}

.form-container, .result-container {
    background-color: var(--surface-color);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px var(--shadow-color);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-row {
    display: flex;
    gap: 1rem;
}

.form-row .form-group {
    flex: 1;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-secondary);
}

input, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-family: inherit;
    font-size: 1rem;
}

input:focus, textarea:focus {
    outline: none;
    border-color: var(--primary-color);
}

button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

button:hover {
    background-color: var(--primary-dark);
}

#generate-btn {
    width: 100%;
}

.hidden {
    display: none;
}

#loading {
    text-align: center;
    padding: 2rem;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid var(--border-color);
    border-top: 5px solid var(--primary-color);
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

#result h2 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.image-container {
    margin-bottom: 1.5rem;
    text-align: center;
}

.image-container img {
    max-width: 100%;
    border-radius: 4px;
    box-shadow: 0 2px 4px var(--shadow-color);
}

.actions {
    display: flex;
    gap: 1rem;
}

.actions button {
    flex: 1;
}

#download-btn {
    background-color: var(--secondary-color);
    color: var(--text-primary);
}

#download-btn:hover {
    background-color: #02c4b2;
}

#error {
    color: var(--error-color);
    text-align: center;
    padding: 2rem;
}

.error-details {
    margin-top: 0.5rem;
    font-family: monospace;
    background-color: #ffeeee;
    padding: 1rem;
    border-radius: 4px;
    text-align: left;
    white-space: pre-wrap;
    overflow-x: auto;
}

footer {
    text-align: center;
    margin-top: 2rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
}
    """, media_type="text/css")

@fastapi_app.get("/static/js/script.js")
async def get_js():
    return Response(content="""
// script.js - JavaScript for the Stable Diffusion web interface

document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const form = document.getElementById('generation-form');
    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const generatedImage = document.getElementById('generated-image');
    const downloadBtn = document.getElementById('download-btn');
    const newGenerationBtn = document.getElementById('new-generation-btn');
    
    // Add event listeners
    form.addEventListener('submit', handleFormSubmit);
    downloadBtn.addEventListener('click', handleDownload);
    newGenerationBtn.addEventListener('click', resetForm);
    
    // Handle form submission
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Show loading state
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        // Get form data
        const formData = new FormData(form);
        const params = new URLSearchParams();
        
        // Add form data to URL params
        for (const [key, value] of formData.entries()) {
            params.append(key, value);
        }
        
        try {
            // Send request to the API
            const response = await fetch(`/generate?${params.toString()}`, {
                method: 'POST',
            });
            
            // Check if the request was successful
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }
            
            // Parse the response
            const data = await response.json();
            
            // Display the generated image using base64 data
            if (data.base64_image) {
                generatedImage.src = `data:image/png;base64,${data.base64_image}`;
                loadingDiv.classList.add('hidden');
                resultDiv.classList.remove('hidden');
                generateBtn.disabled = false;
            } else {
                // Fallback to URL if base64 is not available
                generatedImage.src = data.image_url;
                generatedImage.onload = () => {
                    loadingDiv.classList.add('hidden');
                    resultDiv.classList.remove('hidden');
                    generateBtn.disabled = false;
                };
                
                // Handle image load error
                generatedImage.onerror = () => {
                    loadingDiv.classList.add('hidden');
                    errorDiv.classList.remove('hidden');
                    errorMessage.textContent = "Failed to load the generated image. Please try again.";
                    generateBtn.disabled = false;
                };
            }
        } catch (error) {
            console.error('Error:', error);
            loadingDiv.classList.add('hidden');
            errorDiv.classList.remove('hidden');
            errorMessage.textContent = error.message || 'Unknown error occurred';
            generateBtn.disabled = false;
        }
    }
    
    // Handle image download
    function handleDownload() {
        const imageUrl = generatedImage.src;
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `stable-diffusion-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Reset the form for a new generation
    function resetForm() {
        resultDiv.classList.add('hidden');
        form.reset();
    }
});
    """, media_type="application/javascript")

@fastapi_app.get("/api")
async def api_root():
    return {"message": "Welcome to the Stable Diffusion API"}

@fastapi_app.post("/generate")
async def generate_image(prompt: str, width: int = 1024, height: int = 1024, num_inference_steps: int = 30, guidance_scale: float = 8.0):
    """
    Generate an image from a text prompt using Stable Diffusion 3.5.
    
    Args:
        prompt: The text prompt to generate an image from
        width: The width of the generated image
        height: The height of the generated image
        num_inference_steps: Number of denoising steps
        guidance_scale: Guidance scale for the diffusion process
    
    Returns:
        A URL to the generated image
    """
    try:
        # Generate a unique ID for this image
        image_id = str(uuid.uuid4())
        
        # Generate the image
        image_path = f"{VOLUME_PATH}/{image_id}.png"
        
        # Print debug information
        print(f"Generating image with prompt: '{prompt}'")
        print(f"Parameters: width={width}, height={height}, steps={num_inference_steps}, guidance={guidance_scale}")
        print(f"Image will be saved to: {image_path}")
        
        # Call the Modal function to generate the image
        try:
            result = sd_model.generate_image.remote(
                prompt=prompt,
                output_path=image_path,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            print(f"Image generation completed successfully")
            
            # Return both the URL and the base64-encoded image
            return {
                "image_url": f"/images/{image_id}.png", 
                "base64_image": result["base64_image"],
                "status": "success"
            }
        except Exception as e:
            print(f"Error in generate_image.remote: {str(e)}")
            raise
        
    except Exception as e:
        print(f"Error in generate_image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@fastapi_app.get("/images/{image_id}")
async def get_image(image_id: str):
    """
    Get a generated image by ID.
    
    Args:
        image_id: The ID of the image to get
    
    Returns:
        The image file
    """
    image_path = f"{VOLUME_PATH}/{image_id}"
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        try:
            contents = os.listdir(VOLUME_PATH)
            print(f"Contents of {VOLUME_PATH} directory: {contents}")
        except Exception as e:
            print(f"Error listing directory contents: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")
    
    return FileResponse(image_path)

# Mount the FastAPI app to Modal
@app.function(
    image=image, 
    volumes={VOLUME_PATH: volume},
    secrets=[hf_secret] if hf_secret is not None else []
)
@modal.asgi_app()
def serve_app():
    # Create directories before serving the app
    create_directories.remote()
    return fastapi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000) 