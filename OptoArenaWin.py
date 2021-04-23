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
import Rig
import MyUART
import Program
import ntpath

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

class COMChoiceWindow(QtWidgets.QDialog):
    def __init__(self):
        super(COMChoiceWindow, self).__init__()
        uic.loadUi("comdialog.ui", self)
        self.LoadSerialPorts()

    
    def LoadSerialPorts(self):
        thePort = MyUART.MyUART()
        ports=thePort.GetAvailablePorts()
        self.comboBox.clear()
        if(len(ports)==0):
            self.comboBox.addItem("None")
        for p in ports:
            self.comboBox.addItem(p)
        
class MyMainWindow(QtWidgets.QMainWindow):
    def __init__( self):   
        self.version ="4.0.0"
        self.theRig = Rig.OptoLifespanRig(1)
        super(MyMainWindow,self).__init__()        
        uic.loadUi("mainwindow.ui",self)

        self.COMWindow = COMChoiceWindow()
        #tmp2 = "QTextEdit {background-color: "+self.defaultBackgroundColor+"}"
        #tmp3 = "QListWidget {background-color: "+self.defaultBackgroundColor+"}"
        #self.MessagesTextEdit.setStyleSheet(tmp2)        
        #self.ProgramTextEdit.setStyleSheet(tmp2)     
        #self.ProgramPreviewTextBox.setStyleSheet(tmp2)       
        self.statusmessageduration=5000
        self.MakeConnections()
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

        self.currentLocalProgramName="None Loaded"
        self.currentLocalProgramPath="None Loaded"

        if(self.COMWindow.exec_()):
            portChoice = self.COMWindow.comboBox.currentText()
            if(portChoice=="None"):
                sys.exit()    
            self.theRig.thePort.Open(portChoice)
            self.theRig.SetAsFirstRigInList()
            self.UpdateStatus()
            self.UpdateRemoteProgram()
        else:              
            sys.exit()

    def UpdateStatus(self):
        self.SoftwareLabel.setText(self.version)
        self.IDLabel.setText(str(self.theRig.ID))
        self.LocalTimeLabel.setText(datetime.datetime.today().strftime("%B %d, %Y %H:%M:%S"))                    
        self.RTCTimeLabel.setText(self.theRig.GetRemoteRTCString())
        self.FirmwareLabel.setText(self.theRig.GetVersionInformationString()[1:])
        self.UpdateErrors(True)

    def UpdateRemoteProgram(self):
        ss= self.theRig.GetRemoteProgramStringForGUI()
        self.RemoteProgramTextEdit.setPlainText(ss)
        self.ComparePrograms()

   
    def UpdateGUI(self):
        self.statusLabel.setText(datetime.datetime.today().strftime("%B %d,%Y %H:%M:%S"))                    

    def MakeConnections(self):                     
        self.ClearErrorsButton.clicked.connect(self.ClearErrorsClicked)
        self.SyncTimeButton.clicked.connect(self.SyncTimeClicked)
        self.ShowProtocolButton.clicked.connect(self.ProtocolButtonClicked)
        self.GetButton.clicked.connect(self.GetButtonClicked)
        self.StageButton.clicked.connect(self.StageButtonClicked)
        self.StopButton.clicked.connect(self.StopButtonClicked)
        self.RemoteSaveButton.clicked.connect(self.RemoteSaveButtonClicked)
        self.RemoteLoadButton.clicked.connect(self.RemoteLoadButtonClicked)
        self.ClearButton.clicked.connect(self.ClearButtonClicked)
        self.LocalLoadButton.clicked.connect(self.LocalLoadButtonClicked)
        self.UploadButton.clicked.connect(self.UploadButtonClicked)
        self.LocalSaveButton.clicked.connect(self.LocalSaveButtonClicked)
        self.Error1CheckBox.setChecked(True)

    def UpdateErrors(self,updateFirst):
        if updateFirst==True:
            self.theRig.GetCurrentErrors()
        
        if self.theRig.currentErrors & 0x01:
            self.Error1CheckBox.setChecked(True)
        else:
            self.Error1CheckBox.setChecked(False)

        if self.theRig.currentErrors & 0x02:
            self.Error2CheckBox.setChecked(True)
        else:
            self.Error2CheckBox.setChecked(False)
        
        if self.theRig.currentErrors & 0x04:
            self.Error3CheckBox.setChecked(True)
        else:
            self.Error3CheckBox.setChecked(False)

        if self.theRig.currentErrors & 0x08:
            self.Error4CheckBox.setChecked(True)
        else:
            self.Error4CheckBox.setChecked(False)

        if self.theRig.currentErrors & 0x10:
            self.Error5CheckBox.setChecked(True)
        else:
            self.Error5CheckBox.setChecked(False)
        
        if self.theRig.currentErrors & 0x20:
            self.Error6CheckBox.setChecked(True)
        else:
            self.Error6CheckBox.setChecked(False)

        if self.theRig.currentErrors & 0x40:
            self.Error7CheckBox.setChecked(True)
        else:
            self.Error7CheckBox.setChecked(False)

        if self.theRig.currentErrors & 0x80:
            self.Error8CheckBox.setChecked(True)
        else:
            self.Error8CheckBox.setChecked(False)        

    def ClearErrorsClicked(self):
        if self.theRig.SendClearErrors():
            self.ConsoleTextEdit.append("Clear errors signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Clear errors signal sent but not acknowledged.")
        self.UpdateStatus()

    def SyncTimeClicked(self):
        s=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if self.theRig.SendRTCSet(s):                    
            self.ConsoleTextEdit.append("New datetime sent and acknowledged.")         
            self.UpdateErrors(False)  
            self.UpdateStatus()
        else:
            self.ConsoleTextEdit.append("Problem sending new date and time.")
    def ProtocolButtonClicked(self):
        pass
    def GetButtonClicked(self):
        self.UpdateRemoteProgram()
    def StageButtonClicked(self):
        if self.theRig.SendStageProgram():
            self.ConsoleTextEdit.append("Stage program signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Stage program signal sent but not acknowledged.")
        self.UpdateErrors(False)
        self.UpdateRemoteProgram()
    def StopButtonClicked(self):
        if self.theRig.SendStopProgram():
            self.ConsoleTextEdit.append("Stop program signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Stop program signal sent but not acknowledged.")
        self.UpdateErrors(False)
        self.UpdateRemoteProgram()
    def RemoteLoadButtonClicked(self):
        if self.theRig.SendLoadProgram():
            self.ConsoleTextEdit.append("Load program signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Load program signal sent but not acknowledged.")
        self.UpdateErrors(False)
        self.UpdateRemoteProgram()
    def ClearButtonClicked(self):
        if self.theRig.SendClearProgram():
            self.ConsoleTextEdit.append("Clear program signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Clear program signal sent but not acknowledged.")
        self.UpdateErrors(False)
        self.UpdateRemoteProgram()
  
    def ComparePrograms(self):
        if(self.theRig.AreLocalAndRemoteProgramsIdentical()):
            self.ProgramsIdenticalButton.setStyleSheet("background-color: green")
            self.ConsoleTextEdit.append("Local and remote programs are identical.")
        else:
            self.ProgramsIdenticalButton.setStyleSheet("background-color: red")
            self.ConsoleTextEdit.append("Local and remote programs are different.")


    def UploadButtonClicked(self):
        if (self.theRig.UploadLocalProgram()):
            self.ConsoleTextEdit.append("Upload successful and acknowledged.")
            time.sleep(.5)
            self.UpdateErrors(False)
            self.UpdateRemoteProgram()
            self.ComparePrograms()
        else :
            self.ConsoleTextEdit.append("Upload not successful.")       

    def LocalSaveButtonClicked(self):
        try:
            pg = Program.Program()            
            text = self.LocalProgramTextEdit.toPlainText()
            if(pg.LoadLocalProgramFromString(text)):
                self.theRig.LoadLocalProgramFromString(text)
                f = open(self.currentLocalProgramPath, 'w')
                f.write(text)
                f.close()                
                self.ConsoleTextEdit.append("Local program changes saved and applied.")
            else:
                self.ConsoleTextEdit.append("Syntax Error: Local program changes not saved or applied.")
            self.ComparePrograms()

        except:
            self.ConsoleTextEdit.append("Error: Local program changes NOT saved or applied.")

    def LocalLoadButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Text Files (*.txt)", options=options)
        if fileName:
            pg = Program.Program()  
            ## First check to make sure the program is valid.
            ## TODO: Implement better program checking points in the Program class.
            if(pg.LoadLocalProgram(fileName)):
                self.theRig.LoadLocalProgram(fileName)
                self.currentLocalProgramPath=fileName
                self.currentLocalProgramName=ntpath.basename(self.currentLocalProgramPath)
                self.LocalProgramNameLabel.setText(self.currentLocalProgramName)
                f = open(self.currentLocalProgramPath, 'r')
                with f:
                    data = f.read()        
                    self.LocalProgramTextEdit.setPlainText(data)
                    f.close()
                self.ConsoleTextEdit.append("Program loaded.")                
                self.ComparePrograms()
            else:
                self.ConsoleTextEdit.append("Problem loading program.")
                ## Leave the existing program loaded.
                self.ComparePrograms()
        

    def RemoteSaveButtonClicked(self):
        if self.theRig.SendSaveProgram():
            self.ConsoleTextEdit.append("Save program signal sent and acknowledged.")
        else:
            self.ConsoleTextEdit.append("Save program signal sent but not acknowledged.")
        self.UpdateErrors(False)
    
                
def main():
    app = QtWidgets.QApplication(sys.argv)    
    myapp = MyMainWindow()        
    myapp.show()
    sys.exit(app.exec_()) 
    print("Done")
    

if __name__ == "__main__":
    main()
    