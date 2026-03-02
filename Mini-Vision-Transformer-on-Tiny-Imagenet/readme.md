# 🧠 Mini-ViT on Tiny ImageNet: Custom Vision Transformer with Active Learning

An end-to-end machine learning pipeline featuring a **Vision Transformer (ViT)** built entirely from scratch in PyTorch, trained on the Tiny ImageNet dataset using **Distributed Data Parallel (DDP)** for multi-GPU efficiency.

Beyond training, this project features a fully functional **Flask REST API and web frontend** equipped with a continuous learning loop: the model collects user feedback on incorrect predictions, stores them in a buffer, and automatically triggers background incremental learning to update its weights on the fly.

## ✨ Key Features

* **Custom ViT Architecture:** Complete from-scratch PyTorch implementation of Patch Embeddings, Positional Encodings, Multi-Head Self-Attention (MHA), and Encoder blocks.
* **Distributed Training (DDP):** Multi-GPU training script (`train.py`) utilizing `torch.nn.parallel.DistributedDataParallel` for accelerated training.
* **RESTful Flask API:** A lightweight backend serving the model for real-time inference.
* **Active Learning Loop:** A built-in feedback mechanism that saves user corrections to a local buffer. Once the buffer hits 16 images, a background thread performs incremental learning and hot-swaps the live model weights without server downtime.
* **Vanilla Web UI:** A clean, dependency-free HTML/JS interface for uploading images, viewing predictions, and submitting ground-truth feedback.

## 📁 Project Structure

```text
Mini-Vision-Transformer-on-Tiny-Imagenet/
├── backend/
│   ├── artifacts/             # Stores the trained weights (best_vit_ddp.pth, final_checkpoint.pth) and JSON mappings
│   ├── buffer/                # Dynamically stores user-submitted images and feedback logs
│   ├── templates/             # Contains the vanilla HTML frontend (index.html)
│   ├── app.py                 # Flask server and API routing
│   ├── data.py                # Manages the active learning buffer and CSV logging
│   ├── inference.py           # Handles image transformations and model predictions
│   ├── model.py               # The raw PyTorch ViT architecture classes
│   └── updater.py             # Background thread for incremental training and weight hot-swapping
├── train.py                   # Standalone DDP training script for multi-GPU clusters
├── mini-vision-transformer-on-tiny-imagenet-mul-gpu.ipynb # Exploratory notebook and visualization
└── requirements.txt           # Python dependencies

```

## 🚀 Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/MrHeaven1y/Mini-Vision-Transformer-on-Tiny-Imagenet.git
cd Mini-Vision-Transformer-on-Tiny-Imagenet

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Download Tiny ImageNet (Optional for Inference):**
The training script and notebook contain automated cells to download and format the 200-class Tiny ImageNet dataset.

## 🧠 Training the Model (Multi-GPU)

To train the model from scratch using PyTorch's Distributed Data Parallel (DDP), use the standalone training script. It will automatically detect available GPUs and spawn the necessary processes:

```bash
python train.py

```

*Weights will be saved as `best_vit_ddp.pth` and `final_checkpoint.pth`.*

## 🌐 Running the Web App & Inference API

1. Ensure your trained weights (`best_vit_ddp.pth`) and mapping files (`id_to_cls.json`) are inside the `backend/artifacts/` folder.
2. Start the Flask server:
```bash
python backend/app.py

```


3. Open your web browser and navigate to: **`http://127.0.0.1:5000`**

### Using the Active Learning Loop

1. Upload an image via the web UI and click **Predict Image**.
2. If the model predicts incorrectly, enter the true Class ID (0-199) in the feedback section and click **Send Feedback**.
3. The server will save the image to `backend/buffer/images`.
4. Once 16 images are collected, the `IncrementalUpdater` will spin up a background thread, train the model on the new data for 3 epochs using a low learning rate (to prevent catastrophic forgetting), and hot-swap the updated weights into the live inference engine.

## 🛠️ Built With

* **PyTorch** (Deep Learning, DDP, Vision Transformers)
* **Torchvision** (Image Augmentations, Dataset Loaders)
* **Flask** (REST API, Template Rendering)
* **Pandas & PIL** (Buffer Management, Image Processing)
* **Matplotlib** (Metrics Visualization)
