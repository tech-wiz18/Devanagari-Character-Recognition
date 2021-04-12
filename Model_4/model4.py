#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, CSVLogger, EarlyStopping
from tensorflow.keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Flatten, Dense
from tensorflow.keras.layers import Dropout

trainDataGen = ImageDataGenerator(rotation_range = 5,
                                  width_shift_range = 0.1,
                                  height_shift_range = 0.1,
                                  rescale = 1.0/255,
                                  shear_range = 0.2,
                                  zoom_range = 0.2,
                                  horizontal_flip = False,
                                  fill_mode = 'nearest')

testDataGen = ImageDataGenerator(rescale = 1.0/255)

trainGenerator = trainDataGen.flow_from_directory(os.path.join("Splitted_Dataset", "Train"),
                                                  target_size = (32,32),
                                                  batch_size = 32,
                                                  color_mode = "grayscale",
                                                  classes = [str(class_id) for class_id in range(49)],
                                                  class_mode = "categorical")

validationGenerator = testDataGen.flow_from_directory(os.path.join("Splitted_Dataset", "Validation"),
                                                      target_size = (32,32),
                                                      batch_size = 32,
                                                      color_mode = "grayscale",
                                                      classes = [str(class_id) for class_id in range(49)],
                                                      class_mode = "categorical")

model = Sequential()

model.add(Conv2D(filters=32, kernel_size=(5, 5), padding='Same', activation='relu', kernel_initializer='he_uniform',
                 input_shape=(32, 32, 32, 1)))
model.add(Conv2D(32, (3, 3), strides = 1, activation = "relu"))
model.add(Conv2D(filters=32, kernel_size=(5, 5), padding='Same', activation='relu', kernel_initializer='he_uniform'))
model.add(MaxPooling2D((2, 2), strides = (2, 2), padding = "same"))
model.add(Dropout(0.2))

model.add(Conv2D(64, (3, 3), strides = 1, activation = "relu"))
model.add(Conv2D(filters=64, kernel_size=(3, 3), padding='Same', activation='relu', kernel_initializer='he_uniform'))
model.add(Conv2D(filters=64, kernel_size=(3, 3), padding='Same', activation='relu', kernel_initializer='he_uniform'))
model.add(MaxPooling2D((2, 2), strides = (2, 2), padding = "same"))

model.add(Flatten())

model.add(Dense(300, activation="relu", kernel_initializer='he_uniform'))
model.add(Dropout(0.55))

model.add(Dense(100, activation="relu", kernel_initializer='he_uniform'))
model.add(Dropout(0.25))

model.add(Dense(49, activation="softmax"))

model.compile(optimizer = Adam(lr = 1e-3, decay = 1e-5), loss = "categorical_crossentropy", metrics = ['accuracy'])

callbacks = [ReduceLROnPlateau(monitor = 'val_loss', factor = 0.1,
                              patience = 7, min_lr = 1e-5),
             EarlyStopping(patience = 9, # Patience should be larger than the one in ReduceLROnPlateau
                          min_delta = 1e-5),
             CSVLogger("training.log", append = True),
             ModelCheckpoint('backup_last_model.hdf5'),
             ModelCheckpoint('best_val_acc.hdf5', monitor = 'val_accuracy', mode = 'max', save_best_only = True),
             ModelCheckpoint('best_val_loss.hdf5', monitor = 'val_loss', mode = 'min', save_best_only = True)]

model.fit(trainGenerator, epochs = 50, validation_data = validationGenerator, callbacks = callbacks)

model = load_model('best_val_acc.hdf5')
loss, acc = model.evaluate(validationGenerator)

print("Best Accuracy Model:")
print('Loss on Validation Data : ', loss)
print('Accuracy on Validation Data :', '{:.4%}'.format(acc))

model = load_model('best_val_loss.hdf5')
loss, acc = model.evaluate(validationGenerator)

print("Best Loss Model:")
print('Loss on Validation Data : ', loss)
print('Accuracy on Validation Data :', '{:.4%}'.format(acc))


# In[ ]:




