from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import tensorflow as tf
import os
import base64
from io import BytesIO
from PIL import Image
from architecture import InceptionBlock
from flask_cors import CORS

app = Flask(__name__, static_folder='../front-end', static_url_path='/front-end')
CORS(app)

model = None

def load_model():
    global model
    try:
        model = tf.keras.models.load_model('../artifacts/inception_model.keras', custom_objects={'InceptionBlock': InceptionBlock})
        print("Model loaded successfully!")
        model.build((None,28,28,1))
        print("Model is being Build!")
    except Exception as e:
        print(f"Error loading model: {e}")

def preprocess_image(base64_string):
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]
    
    image_data = base64.b64decode(base64_string)
    
    image = Image.open(BytesIO(image_data))
    
    image = image.convert('L')
    
    image = image.resize((28, 28))
    
    img_array = np.array(image)
    img_array = img_array / 255.0
    
  
    img_array = img_array.reshape(1, 28, 28, 1)
    
    return img_array

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/classify', methods=['POST'])
def classify_digit():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        processed_image = preprocess_image(data['image'])

        debug_img = (processed_image[0] * 255).astype(np.uint8)
        Image.fromarray(debug_img.reshape(28, 28)).save('debug_image.png')
        predictions = model.predict(processed_image)
        probabilities = predictions[0].tolist()
        
        predicted_digit = np.argmax(predictions[0])
        print(f"Predicted Digit: {predicted_digit} \t Proba: {probabilities}")

        return jsonify({
            'predicted_digit': int(predicted_digit),
            'probabilities': probabilities
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    load_model()
    
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port)