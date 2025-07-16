# import tensorflow as tf
import os
import numpy as np
import tensorflow as tf
import json
import random
from datetime import datetime


class Check:
    def __init__(self,
                 new_dir_path,
                 prev_num_classes):
        
        self.path = new_dir_path
        self.prev_num_classes = prev_num_classes

    def is_suff(self):
        self.new_classes = len(os.listdir(self.path))

        if self.new_classes >=150:
            return True
        return False
    


class Dataset:
    def __init__(self,image_list,
                 batch_size,
                 image_size,
                 num_classes,
                 repeat,
                 num_parallel_calls,
                 shuffle_buffer,
                 shuffle,
                 ):
    
        self.image_list = image_list
        self.batch_size = batch_size
        self.image_size = image_size
        self.num_classes = num_classes
        self.num_parallel_calls = num_parallel_calls
        self.shuffle = shuffle
        self.repeat = repeat
        self.shuffle_buffer = shuffle_buffer

        self.initiateDs()

    def image_label_gen(self):
        for image,label in self.image_list:
            yield image, label

    def preprocess(self,img_path,
                   label,
                   image_size,
                   num_classes):
        
        img = tf.io.read_file(img_path)
        img = tf.image.decode_image(img,channels=3)
        img = tf.image.resize(img,image_size)
        img = tf.cast(img,tf.float32) / 255.0
        label = tf.one_hot(label, depth=num_classes)
        return img,label
    
    def initiateDs(self):

        output_types = (tf.string,tf.int32)

        dataset = tf.data.Dataset.from_generator(
            lambda : self.image_label_gen(self.image_list),
            output_signature=(
                tf.TensorSpec(shape=(), dtype=tf.string),
                tf.TensorSpec(shape=(),dtype=tf.int32)
            )
        )
        dataset = dataset.map(lambda x,y: self.preprocess(x,y,self.image_size,self.num_classes),num_parallel_calls=self.num_parallel_calls)
        dataset = dataset.batch(self.batch_size)      
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        if self.shuffle>0:
            dataset = dataset.shuffle(self.shuffle_buffer)        
        dataset = dataset.repeat(self.repeat)
        return dataset
    

class IncrementTrain:
    def __init__(self,
                 dir_path,
                 model,
                 batch_size,
                 image_size,
                 prev_labels,
                 repeat,
                 buffer_data_ref,
                 num_parallel_calls,
                 shuffle,
                 shuffle_buffer,
                 split_size
                 ):
        
        self.model = model

        self.batch_size = batch_size
        self.image_size = image_size
        self.num_classes = len(list(prev_labels.keys()))
        self.num_parallel_calls = num_parallel_calls
        self.shuffle = shuffle
        self.repeat = repeat
        self.shuffle_buffer = shuffle_buffer

        self.path = dir_path
        self.buffer_data_ref = buffer_data_ref
        self.labels = list(prev_labels.values()) if isinstance(prev_labels,dict) else prev_labels
        self.label2idx = None
        self.imageList = self.createImageList(self.path,-1)
        self.split_size = split_size
        self.history = None
        self.updated_model_path = None
        if self.imageList == []:
            raise("Nothings' in directory")
        
        if self.model == None:
            raise("NO model here!")


    def updateModel(self,
                    model,
                ):
        last_layer = model.layers[-2].output
        new_output = tf.keras.layers.Dense(self.num_classes,activation='softmax',name='updated_prediction')(last_layer)

        updated_model = tf.keras.Model(inputs=model.input,outputs=new_output)
        return updated_model

    def createImageList(self,
                        dir_path,
                        threshold):

        threshold = -999 if threshold<0 else threshold
        imgList = []
        labels = []
        for folder in os.listdir(dir_path):
            dirname = os.path.join(dir_path,folder)
            labels.append(folder)
            for file in os.listdir(dirname):
                
                file_path = os.path.join(dirname,file)
                imgList.append(
                    (file_path,folder)
                )
                
                
                if threshold != -999 and len(imgList) >= threshold:
                    break
        self.labels = sorted(set(self.labels + labels))
        self.num_classes = len(self.labels)
        self.label2idx = {label:idx for idx,label in enumerate(self.labels)}

        imgList = [(img,self.label2idx[lbl]) for img,lbl in imgList]
        return imgList
                
    def concatenate(self,
                    new_data,
                    old_data,
                    num_prev_points):
        buffer_data = self.createImageList(old_data,
                                           num_prev_points)
        concatenate = buffer_data + new_data
        return concatenate

    def createDataset(self,
                      imageList,
                      buffer_data_ref,
                      split_size=0.8,
                      ):
        
        random.shuffle(imageList)
        
        split = int(len(imageList) * split_size)
        train_data = self.concatenate(imageList[:split],buffer_data_ref[0])
        val_data = self.concatenate(imageList[split:],buffer_data_ref[1]  )      

        train_ds = Dataset(train_data,
                                  batch_size=self.batch_size,
                                  image_size=self.image_size,
                                  num_classes=self.num_classes,
                                  repeat=3,
                                  num_parallel_calls=self.num_parallel_calls,
                                  shuffle_buffer=self.shuffle_buffer,
                                  shuffle=self.shuffle
                                )
        val_ds = Dataset(val_data,
                        batch_size=self.batch_size,
                        image_size=self.image_size,
                        num_classes=self.num_classes,
                        repeat=3,
                        num_parallel_calls=self.num_parallel_calls,
                        shuffle_buffer=self.shuffle_buffer,
                        shuffle=self.shuffle
                    )
         
        steps_per_epoch = np.ceil(len(train_data)/ self.batch_size)
        validation_steps = np.ceil(len(val_data) / self.batch_size)          

        return train_ds,val_ds,steps_per_epoch,validation_steps

    def train(self,
          model,
          train_ds,
          val_ds,
          steps_per_epoch,
          validation_steps,
          epochs,
          optimizer,
          output_dir,
          version,
          metrics,
          callbacks):

        
        output_file = os.path.join(output_dir, f'plant_disease_model_{version}.keras')
        self.updated_model_path = output_file  # store for reloading later


        os.makedirs(output_dir,exist_ok=True)
        
        updated_model = self.updateModel(model=model)
        
       
        
        loss_fn = tf.keras.losses.CategoricalCrossEntropy(label_smoothing=0.1)
        updated_model.compile(optimizer=optimizer,
                      loss=loss_fn,
                      metrics=metrics)
       
        
        self.history = updated_model.fit(train_ds,
                            validation_data=val_ds,
                            epochs=epochs,
                            steps_per_epochs=steps_per_epoch,
                            validation_steps=validation_steps,
                            callbacks=callbacks)
        
        
        updated_model.save(output_file)

        with open('artifacts/labels.json', 'w') as f:
            json.dump({i: label for i, label in enumerate(self.labels)}, f)

    def plots(self):
        pass 

