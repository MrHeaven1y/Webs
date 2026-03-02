import threading
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import HYPERPARAMETERS
from inference import InferenceEngine
from data import DataManager
from updater import IncrementalUpdater

app = Flask(__name__)
# Enable CORS so your vanilla HTML frontend can talk to this API
CORS(app)

# 1. Initialize the central configuration and engines on startup
config = HYPERPARAMETERS()
inference_engine = InferenceEngine(config)
data_manager = DataManager(config)
updater_engine = IncrementalUpdater(config)

print("🚀 Flask API Server is Online.")

@app.route("/", methods=["GET"])
def home():
    # This tells Flask to serve your index.html file!
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Check if an image was actually uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    contents = file.read()
    
    # Pass the raw bytes to the inference engine
    result = inference_engine.predict(contents)
    return jsonify(result)


def run_background_update():
    """Wrapper function to train and then hot-swap the live model."""
    print("Background thread: Triggering incremental learning...")
    updater_engine.train_on_buffer(data_manager)
    inference_engine.load_brain()  # Hot-swap the new weights!


@app.route("/feedback", methods=["POST"])
def feedback():
    # Check for both the image and the corrected label
    if 'image' not in request.files or 'label_id' not in request.form:
        return jsonify({"error": "Missing image or label_id"}), 400
        
    file = request.files['image']
    label_id = int(request.form['label_id'])
    contents = file.read()
    
    # Save the feedback to the buffer
    data_manager.save_feedback(contents, label_id)
    
    # Check if it's time to train
    if data_manager.is_buffer_full():
        # Spin up a separate thread to handle the backpropagation so we don't freeze the web server
        thread = threading.Thread(target=run_background_update)
        thread.start()
        
    return jsonify({"status": "Feedback logged! Model learning..."})

if __name__ == "__main__":
    # Run the server on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)