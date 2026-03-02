import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms as T
import pandas as pd
import os
from PIL import Image
from model import ViT

class BufferDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self): return len(self.data)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.data.iloc[idx, 0])
        image = Image.open(img_path).convert("RGB")
        label = int(self.data.iloc[idx, 1])
        if self.transform: image = self.transform(image)
        return image, label

class IncrementalUpdater:
    def __init__(self, config):
        self.config = config
        self.device = config.device
        
        # 1. Get the absolute path to the backend/ directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Define absolute paths to the artifacts folder
        self.best_model_path = os.path.join(self.base_dir, "artifacts", "best_vit_ddp.pth")
        self.checkpoint_path = os.path.join(self.base_dir, "artifacts", "final_checkpoint.pth")
        
        # Training transforms (We add horizontal flip back in for robustness)
        self.train_transforms = T.Compose([
            T.Resize((64, 64)),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def train_on_buffer(self, data_manager):
        print("🔥 Buffer full! Starting background incremental learning...")
        dataset = BufferDataset(data_manager.log_file, data_manager.buffer_dir, self.train_transforms)
        loader = DataLoader(dataset, batch_size=8, shuffle=True)

        # 3. Initialize the model with the proper config arguments!
        model = ViT(
            d_model=768, 
            n_heads=12, 
            num_classes=200,
            size=self.config.size, 
            patch=self.config.patch, 
            n_layers=self.config.n_layers, 
            dropout=self.config.dropout
        ).to(self.device)
        
        optimizer = optim.AdamW(model.parameters(), lr=1e-5) # Very small LR to prevent forgetting!
        criterion = nn.CrossEntropyLoss()

        # 4. Load the checkpoint using the absolute path
        try:
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
            state_dict = {k.replace('module.', ''): v for k, v in checkpoint["model_state_dict"].items()}
            model.load_state_dict(state_dict)
            
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            for param_group in optimizer.param_groups:
                param_group['lr'] = 1e-5 # Force the small learning rate
        except FileNotFoundError:
            print(f"Warning: Could not find {self.checkpoint_path}. Ensure it exists in the artifacts folder.")
        except Exception as e:
            print(f"Warning: Could not load optimizer state perfectly. Error: {e}")

        model.train()
        # Train for 3 quick epochs on the new batch of data
        for epoch in range(3): 
            for images, labels in loader:
                images, labels = images.to(self.device), labels.to(self.device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

        # 5. Overwrite the old weights with the new ones using absolute paths
        torch.save(model.state_dict(), self.best_model_path)
        torch.save({
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": 80 # Optional tracker
        }, self.checkpoint_path)
        
        data_manager.clear_buffer()
        print("[OK] Incremental learning complete! New weights saved.")