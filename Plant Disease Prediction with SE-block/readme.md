# 🌿 Plant Disease Classifier with SE Block + Incremental Learning

This is a full-stack deep learning web app that predicts **plant diseases** from leaf images using a custom-built **CNN with SE (Squeeze-and-Excitation) Blocks**.  
When it encounters **low-confidence predictions**, it **auto-collects** the data and **re-trains itself** using **incremental learning**.

---

## 🚀 Key Features

✅ CNN model with **SE Block** — boosts feature learning using **channel-wise attention**  
✅ Real-time plant disease classification via web interface  
✅ Stores **low-confidence predictions** for manual labeling  
✅ Automatic **model update** when enough new samples are collected  
✅ Uses buffered old data to prevent catastrophic forgetting  
✅ Modular design with TensorFlow and Flask

---

## 🧠 Why SE Block?

SE Blocks apply **dynamic channel-wise attention** to CNN outputs.  
This lets the model **focus on "what" features are important** for different plant diseases.

🔬 Instead of blindly extracting all features, SE Block:

- **Squeezes** global spatial info into channel descriptors (via GAP)
    
- **Excites** channels using an MLP to **weigh feature maps adaptively**
    

✅ Improved robustness  
✅ Lighter than Transformers  
✅ Ideal for fine-grained tasks like leaf disease detection

```
.
├── backend/
│   ├── server.py                # Flask API server
│   ├── model.py                 # Model with SE blocks (TensorFlow)
│   ├── preprocessing.py         # Image enhancement utilities
│   ├── increment_learning.py    # Incremental training pipeline
│   └── artifacts/
│       ├── plant_disease_model.keras
│       └── labels.json
│
├── frontend/                    # Static files for the UI
├── Dataset/
│   ├── old_datapoints/
│   │   ├── train/
│   │   └── val/
│   └── new_datapoints/         # Saved low-confidence images

```
## 🔁 Incremental Learning Logic

1. Each image is classified through the CNN + SE model
    
2. If confidence `< 0.5`, it:
    
    - Stores the image in `new_datapoints/`
        
    - Accepts **optional user label**
        
3. When `≥ 150` new samples collected:
    
    - Builds a **hybrid dataset** using new + old buffer
        
    - Re-trains final Dense layers (with updated class count)
        
    - Saves updated `.keras` model and `labels.json`
        

---

## 🧪 Model Training Pipeline

- CNN backbone + SE Block
    
- Last Dense layer updated on new class count
    
- One-hot categorical loss with smoothing
    
- Uses `tf.data.Dataset` pipelines with shuffle + prefetch
    
- Separate training and validation steps calculated dynamically
    

---

## 🧾 API

### POST `/api/classify`

**Form-Data:**

- `image`: Leaf image
    
- `label`: Optional user label (string)
    
- `enhance`: Optional preprocessing (`true` or `false`)
    

**Returns:**
```
{
  "class_name": "Tomato___Leaf_Spot",
  "confidence": 0.64,
  "top_predictions": [
    {"class": "Tomato___Leaf_Spot", "probability": 0.64},
    {"class": "Tomato___Septoria", "probability": 0.12},
    ...
  ]
}

```
⚙️ Setup

### 1. Install Requirements

`pip install -r requirements.txt`

### 2. Start the Flask Server

`python backend/server.py`

### 3. Access the Web Interface

`http://localhost:5000`

## 🧾 Model Details

- **Architecture:** Custom CNN with SE Block
    
- **Framework:** TensorFlow 2.x
    
- **Optimizer:** AdamW
    
- **Loss:** Categorical Crossentropy (Label Smoothing = 0.1)
    
- **Input Size:** 256×256×3
    
- **Output:** Softmax over dynamic class count
    

---

## ✅ To-Do / Future Ideas

-  Add UI to label `unlabeled` images in `new_datapoints`
    
-  Use Grad-CAM or saliency for visual explanation
    
-  Export model to TFLite for mobile support
    
-  Add history/plotting endpoint for visualizing training
