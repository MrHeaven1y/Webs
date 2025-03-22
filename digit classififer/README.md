# MNIST Digit Classifier Web Application

A web-based handwritten digit classifier using a trained neural network model with an Inception-inspired architecture. Draw a digit and get real-time predictions with confidence scores.



## Features

- Interactive canvas for drawing digits
- Real-time classification with confidence scores for all digits (0-9)
- Responsive design that works on both desktop and mobile devices
- Visual feedback through confidence bar charts
- Clean, intuitive user interface

## Demo

Try the live demo: [MNIST Digit Classifier Demo](https://your-demo-url.com)

## Project Structure

```
mnist-digit-classifier/
├── backend/
│   ├── app.py                # Flask server
│   ├── architecture.py       # Neural network architecture
│   └── inception_model.keras # Trained model
├── front-end/
│   ├── index.html            # Main HTML file
│   ├── script.js             # Frontend JavaScript
│   └── styles.css            # CSS styling
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- TensorFlow 2.x
- Flask
- Pillow (PIL)
- Node.js (optional, for development)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mnist-digit-classifier.git
   cd mnist-digit-classifier
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Update the model path in `backend/app.py`:
   ```python
   model = tf.keras.models.load_model('path/to/your/inception_model.keras', 
                                     custom_objects={'InceptionBlock': InceptionBlock})
   ```

## Running the Application

1. Start the Flask server:
   ```
   cd backend
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Troubleshooting

### Common Issues

1. **Prediction Always Shows the Same Digit**
   - Check your image preprocessing steps in `app.py`. Make sure the color inversion matches how your model was trained. If your model was trained on black digits with white backgrounds, try removing the line `img_array = 1 - img_array`.
   - Verify the drawing canvas is set up correctly with white stroke on black background.

2. **Server Errors**
   - Ensure the model path is correct in `app.py`.
   - Check that you have the `InceptionBlock` class properly defined in `architecture.py`.

3. **Canvas Not Working**
   - Make sure your browser supports HTML5 Canvas.
   - Check browser console for JavaScript errors.

### Debug Mode

For debugging, you can add the following code to save the processed images before classification:

```python
# In the classify_digit function in app.py
debug_img = (processed_image[0] * 255).astype(np.uint8)
Image.fromarray(debug_img.reshape(28, 28)).save('debug_image.png')
```

## Model Architecture

The classifier uses a custom Inception-inspired architecture with the following key components:

- Input shape: 28x28x1 (grayscale images)
- Multiple Inception blocks with parallel convolutions
- Global average pooling
- Softmax output layer with 10 classes (digits 0-9)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The MNIST dataset creators
- TensorFlow and Keras teams
- Flask framework
