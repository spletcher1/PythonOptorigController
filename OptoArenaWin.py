import sys
import fcntl
import struct
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyudev.pyqt5 import MonitorObserver
from pyudev import Context,Monitor
import datetime
import time
import threading
import platform
import socket
import os
import subprocess
import glob
import shutil

class GUIUpdateThread(QtCore.QThread):
    updateGUISignal = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.keepRunning=True
    def run(self):   
        while self.keepRunning:
            self.updateGUISignal.emit()
            time.sleep(1)
    def StopThread(self):
        self.keepRunning = False

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__( self):   
        super(MyMainWindow,self).__init__()        
        uic.loadUi("mainwindow.ui",self)
        #tmp2 = "QTextEdit {background-color: "+self.defaultBackgroundColor+"}"
        #tmp3 = "QListWidget {background-color: "+self.defaultBackgroundColor+"}"
        #self.MessagesTextEdit.setStyleSheet(tmp2)        
        #self.ProgramTextEdit.setStyleSheet(tmp2)     
        #self.ProgramPreviewTextBox.setStyleSheet(tmp2)       
        self.statusmessageduration=5000
        #self.MakeConnections()
        self.statusLabel = QLabel()  
        self.statusLabel.setFont(QFont('Arial', 11))
        self.statusLabel.setFrameStyle(QFrame.NoFrame)
        self.statusLabel.setFrameShadow(QFrame.Plain)
        self.statusLabel.setText(datetime.datetime.today().strftime("%B %d,%Y %H:%M:%S"))
        self.StatusBar.addPermanentWidget(self.statusLabel)    
        self.StatusBar.setFont(QFont('Arial', 11))        

        self.StatusBar.setStyleSheet('border: 0')
        self.StatusBar.setStyleSheet("QStatusBar::item {border: none;}")    
        
        self.MThread = GUIUpdateThread()
        self.MThread.updateGUISignal.connect(self.UpdateGUI)      
        self.MThread.start()

    def UpdateGUI(self):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)    
    myapp = MyMainWindow()        
    myapp.show()
    sys.exit(app.exec_()) 
    print("Done")
    

if __name__ == "__main__":
    main()
    