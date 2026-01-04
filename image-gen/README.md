# Image Generation with Stable Diffusion

A minimal Python script that generates images from text prompts using the Hugging Face `diffusers` library and the Stable Diffusion 2.1 model.

## Features

- Generate 512x512 images from text prompts
- Uses the free, open-source "stabilityai/stable-diffusion-2-1" model
- Automatic GPU detection and utilization
- Unique filename generation with timestamps
- Interactive command-line interface

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script:**
   ```bash
   python generate_image.py
   ```

## Usage

1. Run the script and wait for the model to load (first run may take several minutes)
2. Enter your text prompt when prompted
3. Wait for image generation (typically 2-5 minutes depending on hardware)
4. Generated images are saved in the `outputs/` folder
5. Type 'quit' to exit the program

## Requirements

- Python 3.7+
- CUDA-compatible GPU recommended (but not required)
- Internet connection for first-time model download

## Example Prompts

- "A serene mountain landscape at sunset"
- "A futuristic city with flying cars"
- "A cute cat playing with yarn"
- "An astronaut riding a bicycle on the moon"

## Notes

- First run will download the model (~4GB) - this only happens once
- GPU usage significantly speeds up generation
- Images are generated at 512x512 resolution
- Each image gets a unique filename with timestamp

