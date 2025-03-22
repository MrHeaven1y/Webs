import tensorflow as tf
from tensorflow.keras.saving import register_keras_serializable

@register_keras_serializable(package="CustomLayers")
class InceptionBlock(tf.keras.layers.Layer):
    def __init__(self, branch1, branch2, branch3, branch4, activation='elu', **kwargs):
        super(InceptionBlock, self).__init__(**kwargs)
        self.branch1 = branch1
        self.branch2 = branch2
        self.branch3 = branch3
        self.branch4 = branch4
        self.activation = activation

    def build(self, input_shape):
        self.branch1_conv = tf.keras.layers.Conv2D(self.branch1, (1, 1), activation=self.activation)
        self.branch2_conv1 = tf.keras.layers.Conv2D(self.branch2[0], (1, 1), activation=self.activation)
        self.branch2_conv2 = tf.keras.layers.Conv2D(self.branch2[1], (3, 3), padding='same', activation=self.activation)
        self.branch3_conv1 = tf.keras.layers.Conv2D(self.branch3[0], (1, 1), activation=self.activation)
        self.branch3_conv2 = tf.keras.layers.Conv2D(self.branch3[1], (5, 5), padding='same', activation=self.activation)
        self.branch4_pool = tf.keras.layers.MaxPooling2D((3, 3), strides=(1, 1), padding='same')
        self.branch4_conv = tf.keras.layers.Conv2D(self.branch4[0], (1, 1), activation=self.activation)

        super(InceptionBlock, self).build(input_shape)

    def call(self, inputs):
        b1 = self.branch1_conv(inputs)
        b2 = self.branch2_conv1(inputs)
        b2 = self.branch2_conv2(b2)
        b3 = self.branch3_conv1(inputs)
        b3 = self.branch3_conv2(b3)
        b4 = self.branch4_pool(inputs)
        b4 = self.branch4_conv(b4)
        return tf.concat([b1, b2, b3, b4], axis=-1)

    def get_config(self):
        config = super(InceptionBlock, self).get_config()
        config.update({
            'branch1': self.branch1,
            'branch2': self.branch2,
            'branch3': self.branch3,
            'branch4': self.branch4,
            'activation': self.activation
        })
        return config
    

