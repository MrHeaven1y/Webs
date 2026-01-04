from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import numpy as np
from model import TensorFlowImageClassifier
from preprocessing import preprocess_image, apply_image_enhancement
import socket
import uuid
from datetime import datetime
from increment_learning import Check, IncrementTrain

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, 'artifacts')
MODEL_NAME = 'plant_disease_model.keras'
LABELS_NAME = 'labels.json'

MODEL_PATH = os.path.join(ARTIFACTS_DIR, MODEL_NAME)
LABELS_PATH = os.path.join(ARTIFACTS_DIR, LABELS_NAME)

NEW_DATASET_DIR = os.path.join(BASE_DIR, r'C:\Users\Heavenly\Desktop\Web Dev\disease\Dataset\new_datapoints')
OLD_DIR = r"C:\Users\Heavenly\Desktop\Web Dev\disease\Dataset\old_datapoints\train"


try:
    classifier = TensorFlowImageClassifier(MODEL_PATH, LABELS_PATH)
    print("[OK] Model loaded successfully")
except Exception as e:
    print(f"[X] Error loading model: {e}")
    classifier = None

@app.route('/')
def serve_index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/classify', methods=['POST'])
def classify_image():
    global classifier
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
    if not ('.' in image_file.filename and 
            image_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'Allowed file types are: png, jpg, jpeg, webp'}), 400

    if classifier is None:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        img_array = preprocess_image(image_file)
        if enhance:
            img_array = apply_image_enhancement(img_array)

        class_id, probabilities = classifier.predict(img_array)

        probabilities = [float(p) for p in probabilities]
        top_indices = np.argsort(probabilities)[-3:][::-1]

        response_data = {
            'class_id': int(class_id),
            'class_name': classifier.labels[str(class_id)] if isinstance(classifier.labels, dict) else classifier.labels[class_id],
            'confidence': float(probabilities[class_id]),
            'top_predictions': [
                {
                    'class': classifier.labels[str(i)] if isinstance(classifier.labels, dict) else classifier.labels[i],
                    'probability': float(probabilities[i])
                }
                for i in top_indices
            ]
        }

        # if response_data['confidence'] < 0.5:
        #     user_label = request.form.get('label', '').strip()
        #     label_folder = user_label if user_label else 'unlabeled'
        #     label_folder = "".join(c for c in label_folder if c.isalnum() or c in (' ', '_', '-'))
        #     label_path = os.path.join(NEW_DATASET_DIR, label_folder)
        #     os.makedirs(label_path, exist_ok=True)
        #     ext = image_file.filename.rsplit('.', 1)[1].lower()
        #     unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
        #     save_path = os.path.join(label_path, unique_name)
        #     image_file.seek(0)
        #     image_file.save(save_path)
        #     print(f"[!] Low-confidence image saved to: {save_path}")

        # if Check(NEW_DATASET_DIR, prev_num_classes=len(classifier.labels)).is_suff():
        #     buffer_data_ref = [
        #         os.path.join(BASE_DIR, "Dataset", "old_datapoints", "train"),
        #         os.path.join(BASE_DIR, "Dataset", "old_datapoints", "val")
        #     ]

        #     incModel = IncrementTrain(
        #         dir_path=NEW_DATASET_DIR,
        #         model=classifier.model,
        #         batch_size=32,
        #         image_size=(256, 256),
        #         prev_labels=classifier.labels,
        #         repeat=1,
        #         buffer_data_ref=buffer_data_ref,
        #         num_parallel_calls=TensorFlowImageClassifier.get_num_parallel_calls(),
        #         shuffle=True,
        #         shuffle_buffer=100,
        #         split_size=0.8
        #     )

        #     train_ds, val_ds, steps_per_epoch, validation_steps = incModel.createDataset(
        #         imageList=incModel.imageList,
        #         buffer_data_ref=buffer_data_ref,
        #         split_size=0.8
        #     )

        #     version = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     model_file = f"plant_disease_model_{version}.keras"
           


        #     incModel.train(
        #         model=classifier.model,
        #         train_ds=train_ds,
        #         val_ds=val_ds,
        #         steps_per_epoch=steps_per_epoch,
        #         validation_steps=validation_steps,
        #         epochs=5,
        #         optimizer=TensorFlowImageClassifier.return_optimizer(),
        #         output_dir=ARTIFACTS_DIR,
        #         version=model_file.replace(".keras", ""),
        #         metrics=['accuracy'],
        #         callbacks=TensorFlowImageClassifier.get_callbacks()
        #     )


        #     classifier = TensorFlowImageClassifier(
        #         model_path=incModel.updated_model_path,
        #         label_path=LABELS_PATH
        #     )


        print(f"Classification result: {response_data['class_name']} ({response_data['confidence']:.2%})")
        return jsonify(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    print(f"\n * Server running at: http://{socket.gethostbyname(socket.gethostname())}:{port}\n")
    app.run(host=host, port=port, debug=True)
