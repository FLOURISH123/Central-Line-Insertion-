# Central Line Insertion Using Convolutional Neural Network with MobileNetV2 Architecture
Tool Classification in Central Line Insertion was done using a Convolutional Neural Network and MobileNetV2 architecture.



Datasets that were used in the project are videos of medical experts performing central line insertion using the central line Tutor System, to have access to all the datasets used, contact The Perk Lab - Laboratory for Percutaneous Surgery.

DataCollection.py file contains the codes of data collection using 3D slicer. 

sequenceSpinBox.py file splits video data into sequence, a sequence is an arrangement of video, audio and graphics (text) clips on the timeline. In other words everything a video consists of. However it is possible to arrange sequences inside other sequences for better organisation. The output of sequenceSpinBox.py is a CSV file containing all label sequences.

The input data which are the frames of image sequence are loaded into the Network.

CNN.py file predicts tools from RGB images and returns a string.

Train_CNN.py module Loads the data from the specified CSV file

         Fold: The fold number given in the CSV file (should be an int),
         
         Set: which set the images and labels make up (should be one of: "Train","Validation", or "Test"),
         
         Returns:
         
         images: The list of images loaded from the files or girderIDs,
         
         imageLabels: a dictionary of the labels for each image, indexed by the label name,
         
         early stopping was used on network to estimate the performance.
         
 RunNeuralNet.py, module runs various neural networks in realtime in Slicer.
 
 Implementation softwares:
 
 3D Slicer (http://download.slicer.org/)
 
Deep-Learn-Live (https://github.com/SlicerIGT/aigt)

Anaconda3.


