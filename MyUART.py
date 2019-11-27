import time
import _thread 
import socketserver 
import serial
import serial.tools.list_ports

class MyUART:
    def __init__(self):        
        self.startByte=0x40 #'@'
        self.endByte=0x23   #'#'
    def Open(self,port):
        self.thePort=serial.Serial(port,115200,timeout=.2)        
    def Write(self,s):
        self.thePort.write(s.encode())
    def WriteByteArray(self,ba):
        self.thePort.write(ba)
    def Read(self,numBytes):
        result=self.thePort.read(numBytes)
        return result
    def GetAvailablePorts(self):
        ports = serial.tools.list_ports.comports()
        available_ports=[]
        for p in ports:
            available_ports.append(p.device)
        return available_ports    