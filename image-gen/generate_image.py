#!/usr/bin/env python3
"""
Minimal image generation script using Stable Diffusion 2.1
Generates images from text prompts and saves them to outputs/ folder
"""

import os
import uuid
from datetime import datetime
from diffusers import StableDiffusionPipeline
import torch

def create_output_folder():
    """Create outputs folder if it doesn't exist"""
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        print("Created outputs/ folder")

def generate_unique_filename():
    """Generate a unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"image_{timestamp}_{unique_id}.png"

def main():
    print("=== Image Generation with Stable Diffusion 2.1 ===")
    print("Loading model... (this may take a few minutes on first run)")
    
    # Load the Stable Diffusion pipeline
    model_id = "stabilityai/stable-diffusion-2-1"
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True
    )
    
    # Move to GPU if available, otherwise use CPU
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        print("Using GPU for generation")
    else:
        print("Using CPU for generation (slower)")
    
    # Create outputs folder
    create_output_folder()
    
    while True:
        print("\n" + "="*50)
        prompt = input("Enter your image prompt (or 'quit' to exit): ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not prompt:
            print("Please enter a valid prompt")
            continue
        
        print(f"\nGenerating image for: '{prompt}'")
        print("This may take a few minutes...")
        
        try:
            # Generate the image
            image = pipe(
                prompt=prompt,
                height=512,
                width=512,
                num_inference_steps=50,
                guidance_scale=7.5
            ).images[0]
            
            # Generate unique filename and save
            filename = generate_unique_filename()
            filepath = os.path.join("outputs", filename)
            image.save(filepath)
            
            print(f"✅ Image saved successfully: {filepath}")
            
        except Exception as e:
            print(f"❌ Error generating image: {str(e)}")
            print("Please try again with a different prompt")

if __name__ == "__main__":
    main()

