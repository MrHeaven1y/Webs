import os
import torch
import io
import json
from PIL import Image
from torchvision import transforms as T
from model import ViT  

class InferenceEngine:
    def __init__(self, config):
        self.config = config
        self.device = config.device
        
        # 1. Get the absolute path to the folder containing this file (backend/)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Build bulletproof absolute paths
        self.weights_path = os.path.join(self.base_dir, "artifacts", "best_vit_ddp.pth")
        self.mapping_path = os.path.join(self.base_dir, "artifacts", "id_to_cls.json")
        
        self.model = ViT(
            d_model=768, 
            n_heads=12, 
            num_classes=200, 
            size=config.size, 
            patch=config.patch, 
            n_layers=config.n_layers, 
            dropout=config.dropout
        ).to(self.device)
        
        self.load_brain()
        
        self.transforms = T.Compose([
            T.Resize((64, 64), interpolation=T.InterpolationMode.BILINEAR),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 3. Use the absolute path here
        with open(self.mapping_path, "r") as f:
            self.mapping = json.load(f)

    def load_brain(self):
        # 4. And use the absolute path here!
        state_dict = torch.load(self.weights_path, map_location=self.device, weights_only=True)
        state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
        self.model.load_state_dict(state_dict)
        self.model.eval()
        print("Inference Engine: Brain loaded.")
        
    def predict(self, image_bytes):
        # Convert raw bytes from the web into a PIL Image, then a Tensor
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transforms(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            conf, pred = torch.max(probs, 1)
        
        idx = str(pred.item())
        return {
            "class_id": idx, 
            "label": self.mapping.get(idx, "Unknown"), 
            "confidence": round(float(conf.item()) * 100, 2)
        }