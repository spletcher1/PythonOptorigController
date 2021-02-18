import time
import _thread 
import socketserver 
import serial
import serial.tools.list_ports

class MyUART:    
    def Open(self,port):
        self.thePort=serial.Serial(port,19200,timeout=20)        
    def Write(self,s):
        self.thePort.write(s.encode())
    def WriteByteArray(self,ba):
        if (self.thePort.out_waiting>0):
            print("out waiting")
            self.thePort.reset_output_buffer()    
        #print(ba)
        self.thePort.write(ba)  
    def Read(self,numBytes):
        result=self.thePort.read(numBytes)
        return result
    def ReadCOBSPacket(self, maxBytes):
        term = bytearray(1)
        term[0]=0x00
        result = self.thePort.read_until(term,maxBytes)
        result = result[:-1]
        #print(result)
        return result
    def GetAvailablePorts(self):
        ports = serial.tools.list_ports.comports()
        available_ports=[]
        for p in ports:
            available_ports.append(p.device)
        return available_ports   
    def ClearInputBuffer(self):
        if (self.thePort.in_waiting>0):
            self.thePort.reset_input_buffer()
    def SetLongTimeOut(self):
        self.thePort.timeout=20
    def SetNormalTimeOut(self):
        self.thePort.timeout=20 
    def SetShortTimeOut(self):
        self.thePort.timeout=0.1    
 
if __name__=="__main__" :
    tmp = MyUART()
    print(tmp.GetAvailablePorts())
