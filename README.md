# Stable Diffusion XL on Modal

A serverless image generation service using Stable Diffusion XL (Illustrious) and Modal. This application allows you to generate high-quality images from text prompts using the power of Stable Diffusion XL, with all the heavy computation handled in the cloud via Modal's serverless platform.

## Features

- Generate images from text prompts using Stable Diffusion XL (Illustrious checkpoint)
- Automatic fallback to base SDXL if the custom checkpoint isn't available
- Serverless deployment with Modal (no infrastructure management)
- GPU acceleration with A10G GPUs for fast image generation
- Clean, responsive web interface
- Customizable generation parameters (size, steps, guidance scale)
- Persistent storage of generated images
- Direct image download
- Higher resolution images (1024x1024 by default)

## Architecture

- **Backend**: FastAPI application running on Modal's serverless platform
- **ML Model**: Stable Diffusion XL with Illustrious checkpoint (fallback to base SDXL)
- **Storage**: Modal Volumes for persistent storage of models and generated images
- **Frontend**: Simple HTML/CSS/JS interface served by the FastAPI application

## Requirements

- Modal account
- Python 3.10+
- Pipenv
- Hugging Face account (for fallback access to base SDXL if needed)

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/stable-diffusion-modal.git
   cd stable-diffusion-modal
   ```

2. Install dependencies using pipenv:
   ```
   pip install pipenv
   pipenv install
   ```

3. Set up Modal:
   ```
   pipenv run python setup_modal.py
   ```
   This will guide you through setting up your Modal account and authentication.

4. Set up Hugging Face token (recommended for fallback):
   ```
   pipenv run python setup_hf_token.py
   ```
   This will prompt you for your Hugging Face token and store it as a Modal secret.
   
   You'll need to create a Hugging Face token if you don't already have one:
   - Go to https://huggingface.co/ and sign in or create an account
   - Go to your profile → Settings → Access Tokens
   - Create a new token (read access is sufficient)

5. Upload the Illustrious XL checkpoint:

   Download the Illustrious XL checkpoint from Hugging Face or another source, then upload it to your Modal volume using the Modal CLI:
   ```bash
   modal volume put stable-diffusion-models illustriousXL_v01.safetensors /models/illustrious_xl.safetensors
   ```
   
   You can verify the upload with:
   ```bash
   modal volume ls stable-diffusion-models /models
   ```

## Deployment

Deploy the application to Modal:
```
pipenv run python deploy.py
```

After deployment, you'll receive a URL where your application is hosted (e.g., `https://username--stable-diffusion-app-serve-app.modal.run`).

## Usage

1. Open the application URL in your web browser
2. Enter a text prompt describing the image you want to generate
3. Adjust parameters if desired:
   - Width and height (default: 1024x1024)
   - Number of inference steps (default: 30)
   - Guidance scale (default: 7.5)
4. Click "Generate Image" and wait for the result
5. Download the generated image or create a new one

## Development

### Project Structure

- `app.py`: Main application entry point and FastAPI implementation
- `deploy.py`: Script to deploy the application to Modal
- `setup_modal.py`: Script to set up Modal authentication
- `setup_hf_token.py`: Script to set up Hugging Face token
- `utils/`: Utility functions

### Local Development

For local development, you can run:
```
pipenv run python app.py
```

This will start the FastAPI application locally, but note that image generation will still run on Modal's cloud infrastructure.

## Technical Details

- The application uses Stable Diffusion XL with the Illustrious checkpoint
- Fallback to base SDXL from Hugging Face if the custom checkpoint isn't available
- Authentication is handled via a Hugging Face token stored as a Modal secret (for fallback)
- Images are generated with PyTorch using half-precision (FP16) for efficiency
- Default image resolution is 1024x1024 for higher quality outputs
- The model runs on A10G GPUs for faster processing
- Generated images are stored in a Modal Volume for persistence
- The web interface communicates with the backend via REST API endpoints
- Images are returned both as files and as base64-encoded data for reliability

## License

MIT