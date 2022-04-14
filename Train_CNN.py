# 881-Project on Central Line Insertion using CNN by Flourish Adebayo
# Train CNN Code File.

# Import all necessary Libaries
import os
import sys
import numpy
import random
import pandas
import argparse
#import girder_client
import tensorflow
import tensorflow.keras
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers
from tensorflow.keras.models import model_from_json
import sklearn
import sklearn.metrics
import cv2
from matplotlib import pyplot as plt
import CNN

FLAGS = None

class Train_CNN:

    #Loads the data from the specified CSV file
    # fold: The fold number given in the CSV file (should be an int)
    # set: which set the images and labels make up (should be one of: "Train","Validation", or "Test")
    # Returns:
    #   images: The list of images loaded from the files or girderIDs
    #   imageLabels: a dictionary of the labels for each image, indexed by the label name
    def loadData(self,fold,set):
        entries = self.dataCSVFile.loc[(self.dataCSVFile["Fold"] == fold) & (self.dataCSVFile["Set"] == set)]
        images = []
        imageLabels = {}
        numFilesWritten = 0
        if "GirderID" in self.dataCSVFile.columns:
            LabelNames = self.dataCSVFile.columns[8:]
            for labelName in LabelNames:
                imageLabels[labelName] = []
            if self.gClient == None:
                self.gClient = girder_client.GirderClient(apiUrl=entries["Girder_URL"][0])
                userName = input("Username: ")
                password = input("Password: ")
                self.gClient.authenticate(username=userName,password=password)

            # tempFileDir is a folder in which to temporarily store the files downloaded from Girder
            # by default the temporary folder is created in the current working directory, but this can
            # be modified as necessary
            username = os.environ['username']
            tempFileDir = os.path.join('C:/Users/',username,'Documents/temp')
            if not os.path.isdir(tempFileDir):
                os.mkdir(tempFileDir)
            for i in entries.index:
                fileID = entries["GirderID"][i]
                fileName = entries["FileName"][i]
                if not os.path.isfile(os.path.join(tempFileDir,fileName)):
                    self.gClient.downloadItem(fileID,tempFileDir)
                    numFilesWritten +=1
                    print(numFilesWritten)
                image = cv2.imread(os.path.join(tempFileDir,fileName))
                resized = cv2.resize(image, (224, 224))
                images.append(numpy.array(resized))
                for labelName in LabelNames:
                    imageLabels[labelName].append(entries[labelName][i])

        else:
            #Files are stored locally on the computer
            LabelNames = self.dataCSVFile.columns[5:]
            for labelName in LabelNames:
                imageLabels[labelName] = []
            for i in entries.index:
                filePath = entries["Folder"][i]
                fileName = entries["FileName"][i]
                fullPath=os.path.join(filePath,fileName)
                image = cv2.imread(fullPath)
                print(fullPath)
                resized = cv2.resize(image, (224, 224))
                images.append(numpy.array(resized))
                for labelName in LabelNames:
                    imageLabels[labelName].append(entries[labelName][i])

        return numpy.array(images),imageLabels

    def convertTextToNumericLabels(self,textLabels,labelValues):
        numericLabels =[]
        for i in range(len(textLabels)):
            label = numpy.zeros(len(labelValues))
            labelIndex = numpy.where(labelValues == textLabels[i])
            label[labelIndex] = 1
            numericLabels.append(label)
        return numpy.array(numericLabels)

    def saveTrainingInfo(self,foldNum,saveLocation,trainingHistory,results):
        LinesToWrite = []
        folds = "Fold " + str(foldNum) +"/"+ str(self.numFolds)
        modelType = "\nNetwork type: " + str(self.networkType)
        LinesToWrite.append(modelType)
        datacsv = "\nData CSV: " + str(FLAGS.data_csv_file)
        LinesToWrite.append(datacsv)
        numEpochs = "\nNumber of Epochs: " + str(self.numEpochs)
        LinesToWrite.append(numEpochs)
        batch_size = "\nBatch size: " + str(self.batch_size)
        LinesToWrite.append(batch_size)
        LearningRate = "\nLearning rate: " + str(self.learning_rate)
        LinesToWrite.append(LearningRate)
        LossFunction = "\nLoss function: " + str(self.loss_Function)
        LinesToWrite.append(LossFunction)
        trainStatsHeader = "\n\nTraining Statistics: "
        LinesToWrite.append(trainStatsHeader)
        trainLoss = "\n\tFinal training loss: " + str(trainingHistory["loss"][len(trainingHistory)-1])
        LinesToWrite.append(trainLoss)
        for i in range(len(self.metrics)):
            trainMetrics = "\n\tFinal training " + self.metrics[i] + ": " + str(trainingHistory[self.metrics[i]][len(trainingHistory)-1])
            LinesToWrite.append(trainMetrics)
        trainLoss = "\n\tFinal validation loss: " + str(trainingHistory["val_loss"][len(trainingHistory) - 1])
        LinesToWrite.append(trainLoss)
        for i in range(len(self.metrics)):
            valMetrics = "\n\tFinal validation " + self.metrics[i] + ": " + str(trainingHistory["val_"+self.metrics[i]][len(trainingHistory) - 1])
            LinesToWrite.append(valMetrics)
        testStatsHeader = "\n\nTesting Statistics: "
        LinesToWrite.append(testStatsHeader)
        testLoss = "\n\tTest loss: " + str(results[0])
        LinesToWrite.append(testLoss)
        for i in range(len(self.metrics)):
            testMetrics = "\n\tTest " + self.metrics[i] + ": " + str(results[i+1])
            LinesToWrite.append(testMetrics)
        LinesToWrite.append("\n" + str(self.confMat))

        with open(os.path.join(saveLocation,"trainingInfo.txt"),'w') as f:
            f.writelines(LinesToWrite)

    def saveTrainingPlot(self,saveLocation,history,metric):
        fig = plt.figure()
        plt.plot([x for x in range(self.numEpochs)], history[metric], 'bo', label='Training '+metric)
        plt.plot([x for x in range(self.numEpochs)], history["val_" + metric], 'b', label='Validation '+metric)
        plt.title('Training and Validation ' + metric)
        plt.xlabel('Epochs')
        plt.ylabel(metric)
        plt.legend()
        plt.savefig(os.path.join(saveLocation, metric + '.png'))
        plt.close(fig)

    def train(self):
        self.saveLocation = FLAGS.save_location
        self.networkType = os.path.basename(os.path.dirname(self.saveLocation))
        self.dataCSVFile = pandas.read_csv(FLAGS.data_csv_file)
        self.numEpochs = FLAGS.num_epochs
        self.batch_size = FLAGS.batch_size
        self.learning_rate = FLAGS.learning_rate
        self.optimizer = tensorflow.keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.loss_Function = FLAGS.loss_function
        self.metrics = FLAGS.metrics.split(",")
        self.numFolds = self.dataCSVFile["Fold"].max() + 1
        self.gClient = None
        network = CNN.CNN()
        for fold in range(0,self.numFolds):
            foldDir = self.saveLocation+"_Fold_"+str(fold)
            os.mkdir(foldDir)
            labelName = self.dataCSVFile.columns[-1] #This should be the label that will be used to train the network

            trainImages,trainLabels = self.loadData(fold,"Train")
            valImages,valLabels = self.loadData(fold,"Validation")
            testImages,testLabels = self.loadData(fold,"Test")

            labelValues = numpy.array(sorted(self.dataCSVFile[labelName].unique()))
            numpy.savetxt(os.path.join(foldDir,"labels.txt"),labelValues,fmt='%s',delimiter=',')

            numericTrainLabels = self.convertTextToNumericLabels(trainLabels[labelName],labelValues)
            numericValLabels = self.convertTextToNumericLabels(valLabels[labelName], labelValues)
            numericTestLabels = self.convertTextToNumericLabels(testLabels[labelName], labelValues)

            model = network.createModel((224,224,3),num_classes=len(labelValues))
            model.compile(optimizer = self.optimizer, loss = self.loss_Function, metrics = self.metrics)
            history = model.fit(x=trainImages,
                                y=numericTrainLabels,
                                validation_data=(valImages,numericValLabels),
                                batch_size = self.batch_size,
                                epochs = self.numEpochs)

            results = model.evaluate(x = testImages,
                                     y = numericTestLabels,
                                     batch_size = self.batch_size)
            predictions = model.predict(x=testImages)
            predictions = numpy.argmax(predictions, axis=-1)
            trueLabels = numpy.argmax(numericTestLabels, axis=-1)
            self.confMat = sklearn.metrics.confusion_matrix(trueLabels, predictions)
            
            network.saveModel(model,foldDir)
            self.saveTrainingInfo(fold,foldDir,history.history,results)
            self.saveTrainingPlot(foldDir,history.history,"loss")
            for metric in self.metrics:
                self.saveTrainingPlot(foldDir,history.history,metric)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--save_location',
      type=str,
      default='',
      help='Name of the directory where the models and results will be saved'
  )
  parser.add_argument(
      '--data_csv_file',
      type=str,
      default='',
      help='Path to the csv file containing locations for all data used in training'
  )
  parser.add_argument(
      '--num_epochs',
      type=int,
      default=15, #I used 5, 10, and 15 epochs variation
      help='number of epochs used in training'
  )
  parser.add_argument(
      '--batch_size',
      type=int,
      default=32, # I used 8, 16, and 32 batch sizes
      help='type of output your model generates'
  )
  parser.add_argument(
      '--learning_rate',
      type=float,
      default=0.00001, #I used 0.001,0.0001 and 0.00001 Learning rates
      help='Learning rate used in training'
  )
  parser.add_argument(
      '--loss_function',
      type=str,
      default='categorical_crossentropy',
      help='Name of the loss function to be used in training (see keras documentation).'
  )
  parser.add_argument(
      '--metrics',
      type=str,
      default='accuracy',
      help='Metrics used to evaluate model.'
  )
FLAGS, unparsed = parser.parse_known_args()


# Early stopping utilization to avoid overfitting.
class Early_Stopping:
    
    def __init__(self, sess, saver, epochs_to_wait, metric_name):
        self.sess = sess
        self.saver = saver
        self.epochs_to_wait = epochs_to_wait
        self.metric_list = []
        self.counter = 0
        self.metric_name = metric_name
        
    def add_metric(self):
        self.metric_list.append(self.metric)
        
    def save_best_model(self,metric):
        self.metric = metric
        self.add_metric()
        
        if max(self.metric_list) == self.metric_list[-1]:
            self.best_metric = self.metric
            print('{} improved from {} to {}'.format(self.metric_name, self.metric_list[-2], self.best_metric))
            self.saver.save(self.sess, '/tmp/checkpoints/')
            self.counter = 0
            
        else:
            print('{} did not improve since test {} was {}'.format(self.metric_name, self.metric_name, self.best_metric))
            self.counter += 1

tm = Train_CNN()
tm.train()
