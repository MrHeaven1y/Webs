import tensorflow as tf
import numpy as np
import json
import os

class SEBlock(tf.keras.layers.Layer):
    def __init__(self,channels,reduction=16,**kwargs):
        super(SEBlock,self).__init__(**kwargs)
        self.channels = channels
        self.reduction = reduction

    def build(self,input_shape):
        self.global_pool = tf.keras.layers.GlobalAveragePooling2D()
        self.fc1 = tf.keras.layers.Dense(self.channels//self.reduction,activation='relu')
        self.fc2 = tf.keras.layers.Dense(self.channels,activation='sigmoid')
        self.reshape = tf.keras.layers.Reshape((1,1,self.channels))
        super(SEBlock,self).build(input_shape)

    def call(self,inputs):
        x = self.global_pool(inputs)
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.reshape(x)
        return tf.keras.layers.Multiply()([inputs,x])



class TensorFlowImageClassifier:
    def __init__(self, model_path, label_path=None):
        
        """
        Initialize the TensorFlow image classifier
        
        Args:
            model_path: Path to the saved TensorFlow model
            labels: List of class labels
        """
        self.model = self._load_model(model_path)
        self.labels = self.load_labels(label_path)
    
    @staticmethod
    def _load_model(model_path):
        try:
            # Try loading as Keras model first
            return tf.keras.models.load_model(model_path,custom_objects={'SEBlock': SEBlock},compile=False)
        except Exception as e:
                print(f"Model loading failed: {str(e)}")
                raise

    @staticmethod
    def load_labels(path):
        with open(path,'r') as f:
            labels = json.load(f)
        return labels
    
    @staticmethod
    def return_optimizer():
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=5e-5,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-7,
            amsgrad=False
        )
        return optimizer

    @staticmethod
    def get_num_parallel_calls():
        return tf.data.AUTOTUNE
    

    @staticmethod
    def get_callbacks():
 
        lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=4, verbose=1, min_lr=1e-10
        )
 
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',          # Watch validation loss
            patience=5,                  # Stop after 5 epochs with no improvement
            min_delta=1e-4,              # Minimum change to qualify as an improvement
            restore_best_weights=True,  # Roll back to the best weights
            mode='min',                 # We want to minimize val_loss
            verbose=1
        )
            
        return [lr_scheduler,early_stopping]

    def predict(self, img_array):
        
        """
        Make prediction on preprocessed image
        
        Args:
            img_array: Preprocessed image array with shape [1, height, width, channels]
            
        Returns:
            class_id: Predicted class ID
            probabilities: List of class probabilities
        """
        
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)
            
        predictions = self.model.predict(img_array)
        
        
        if len(predictions.shape) == 2:  
            class_id = np.argmax(predictions[0])
            probabilities = predictions[0].tolist()
        else:  
            class_id = np.argmax(predictions)
            probabilities = predictions.flatten().tolist()
            
        return class_id, probabilities


if __name__=='__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, 'artifacts', 'VGG_net_kaggle.keras')
    LABELS_PATH = os.path.join(BASE_DIR, 'artifacts', 'labels.json')

    classifier = TensorFlowImageClassifier(MODEL_PATH, LABELS_PATH)