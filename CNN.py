# 881-Project on Central Line Insertion using CNN with MobileNetV2 Architecture by Flourish Adebayo
# CNN-MobileNetV2 Code File.

# Import all necessary Libaries
import os
import cv2
import sys
import numpy
import tensorflow
import tensorflow.keras
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers
from tensorflow.keras.models import model_from_json
#Add any additional modules that your network needs

''' 
Model description: 
     CNN predicts tools from RGB images and returns a string.
'''

class CNN():
    def __init__(self):
        
        self.cnnModel = None
        self.labels = None

    def loadModel(self,modelFolder,modelName):
       
        structureFileName = 'mobileNetv2.json'
        weightsFileName = 'mobileNetv2.h5'
        modelFolder = modelFolder.replace("'","")
        with open(os.path.join(modelFolder, structureFileName), "r") as modelStructureFile:
            JSONModel = modelStructureFile.read()
        self.cnnModel = model_from_json(JSONModel)
        self.cnnModel.load_weights(os.path.join(modelFolder, weightsFileName))
        self.labels = self.labels.split(sep="\n")
        toolLabels = ['anesthetic', 'catheter', 'dilator', 'guidewire','guidewire_casing', 'nothing', 'scalpel', 'syringe']
        self.labels=toolLabels

    def predict(self,image):
        
        # softmax output
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(image, (224, 224))
        resized = numpy.expand_dims(resized, axis=0)
        classification = self.cnnModel.predict(numpy.array(resized))
        labelIndex = numpy.argmax(classification)
        label = self.labels[labelIndex]
        networkOutput = str(label) + str(classification)
        return networkOutput

    def createModel(self,imageSize,num_classes):
       
        # create a MobileNetV2 model and initialize the model with weights from training on ImageNet
        model = tensorflow.keras.models.Sequential()
        model.add(MobileNetV2(weights='imagenet',include_top=False,input_shape=imageSize))
        model.add(layers.GlobalAveragePooling2D())
        model.add(layers.Dense(512,activation='relu'))
        model.add(layers.Dense(num_classes,activation='softmax'))
        return model

    def saveModel(self,trainedModel,saveLocation):
        JSONmodel = trainedModel.to_json()
        structureFileName = 'mobileNetv2.json'
        weightsFileName = 'mobileNetv2.h5'
        with open(os.path.join(saveLocation,structureFileName),"w") as modelStructureFile:
            modelStructureFile.write(JSONmodel)
        trainedModel.save_weights(os.path.join(saveLocation,weightsFileName))
     
     
