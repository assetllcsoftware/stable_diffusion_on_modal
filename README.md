# Stable Diffusion on Modal

A serverless image generation service using Stable Diffusion 3.5 and Modal. This application allows you to generate high-quality images from text prompts using the power of Stable Diffusion 3.5, with all the heavy computation handled in the cloud via Modal's serverless platform.

## Features

- Generate images from text prompts using Stable Diffusion 3.5 (Medium)
- Serverless deployment with Modal (no infrastructure management)
- GPU acceleration with A10G GPUs for fast image generation
- Clean, responsive web interface
- Customizable generation parameters (size, steps, guidance scale)
- Persistent storage of generated images
- Direct image download
- Higher resolution images (1024x1024 by default)

## Architecture

- **Backend**: FastAPI application running on Modal's serverless platform
- **ML Model**: Stable Diffusion 3.5 Medium from Hugging Face
- **Storage**: Modal Volume for persistent storage of generated images
- **Frontend**: Simple HTML/CSS/JS interface served by the FastAPI application

## Requirements

- Modal account
- Python 3.10+
- Pipenv
- Hugging Face account with access to Stable Diffusion 3.5

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

4. Set up Hugging Face token (required for SD 3.5):
   ```
   pipenv run python setup_hf_token.py
   ```
   This will prompt you for your Hugging Face token and store it as a Modal secret.
   
   You'll need to create a Hugging Face token if you don't already have one:
   - Go to https://huggingface.co/ and sign in or create an account
   - Go to your profile → Settings → Access Tokens
   - Create a new token (read access is sufficient)
   - Accept the terms for the Stable Diffusion 3.5 model at https://huggingface.co/stabilityai/stable-diffusion-3.5-medium

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
   - Guidance scale (default: 8.0)
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

- The application uses Stable Diffusion 3.5 Medium directly from Hugging Face
- Authentication is handled via a Hugging Face token stored as a Modal secret
- Images are generated with PyTorch using half-precision (FP16) for efficiency
- Default image resolution is 1024x1024 for higher quality outputs
- The model runs on A10G GPUs for faster processing
- Generated images are stored in a Modal Volume for persistence
- The web interface communicates with the backend via REST API endpoints
- Images are returned both as files and as base64-encoded data for reliability

## License

MIT