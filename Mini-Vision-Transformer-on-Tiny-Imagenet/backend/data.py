import os
import uuid
import pandas as pd
from PIL import Image
import io

class DataManager:
    def __init__(self, config):
        self.config = config
        
        # 1. Get the absolute path to the folder where data.py lives (backend/)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Build absolute paths locking the buffer inside the backend folder
        self.buffer_dir = os.path.join(self.base_dir, "buffer", "images")
        self.log_file = os.path.join(self.base_dir, "buffer", "feedback_log.csv")
        
        # Create folders if they don't exist
        os.makedirs(self.buffer_dir, exist_ok=True)
        if not os.path.exists(self.log_file):
            pd.DataFrame(columns=["filename", "label_id"]).to_csv(self.log_file, index=False)
    def save_feedback(self, image_bytes, label_id):
        # Generate a random unique filename for the image
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(self.buffer_dir, filename)
        
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image.save(filepath)
        
        # Log it in the CSV
        df = pd.DataFrame([{"filename": filename, "label_id": label_id}])
        df.to_csv(self.log_file, mode='a', header=False, index=False)
        print(f"Saved new feedback image: {filename}")
        
    def is_buffer_full(self):
        df = pd.read_csv(self.log_file)
        # Let's trigger training every time we collect 16 new images
        return len(df) >= 16 

    def clear_buffer(self):
        # Nuke the buffer after training so we don't overfit to old feedback
        for f in os.listdir(self.buffer_dir):
            os.remove(os.path.join(self.buffer_dir, f))
        pd.DataFrame(columns=["filename", "label_id"]).to_csv(self.log_file, index=False)