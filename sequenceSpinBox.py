# 881-Project on Central Line Insertion using CNN by Flourish Adebayo
# Sequence Spin Box Code File.
# Import all necessary Libaries

import numpy
import vtk, qt, ctk, slicer

class sequenceSpinBox(qt.QDoubleSpinBox):
    def __init__(self,parent=None):
        super().__init__()
        
        

    def setValueRange(self,values):
        self.valueRange = values
        
        

    def textFromValue(self,value):
        text = "%.2f" % float(self.valueRange[int(value)])
        return(text)
    
    
    
    def valueFromText(self,text):
        value = int(self.valueRange.index(text))
        return value
