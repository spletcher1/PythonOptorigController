import time
import _thread 
import socketserver 
import serial

class MyUART:
    def __init__(self, ID):
        #self.thePort=serial.Serial('/dev/ttyS0',19200)
        self.thePort=serial.Serial('/dev/ttyUSB0',115200,timeout=1000)
        self.ID = ID
        self.startByte=0x40 #'@'
        self.endByte=0x23   #'#'
    def Write(self,s):
        self.thePort.write(s.encode())
    def StartListening(self):
        while True:
            ser_byte=self.thePort.read()
            if(ser_byte[0]==self.startByte):
                ser_bytes=self.thePort.read(2) 
                if(ser_bytes[1]==self.endByte and ser_bytes[0]==self.ID):
                    
                    print(tmp)
                    self.Write(tmp)
                else:
                    print('ID=%d is not for me or endBye (=%d) incorrect.' % (ser_bytes[0],  ser_bytes[1]))
                    #print(ser_bytes)
            else:
                print('Bad Packet %d', ser_byte[0])

if __name__=="__main__" :
    uart = MyUART(1)
    while True:
        uart.Write("Hi there::")
        print("Hi there::")
        #tsl.PrintAllInfo()
        time.sleep(2)
    