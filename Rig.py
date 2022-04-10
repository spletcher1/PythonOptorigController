import time
import _thread 
import socketserver 
import MyUART
import Program
import datetime
from cobs import cobs

class OptoLifespanRig:
    def __init__(self, ID):
        self.ID = ID
        self.thePort=MyUART.MyUART()
        self.startByte=0x40 
        self.endByte=0x00   #'A'#'@'
        self.remoteProgram = Program.Program()
        self.localProgram = Program.Program()
        self.currentErrors=0
    def SetAsFirstRigInList(self):
        rigNumbers=range(1,30)        
        results = {}        
        for num in rigNumbers:
            self.ID = num
            tmp=self.GetVersionInformationString()            
            if tmp!="No response" :              
                self.ID = num              
                return True
            time.sleep(0.10)                      
        return False
    def GetListOfOnlineRigs(self):
        rigNumbers=range(1,30)
        #rigNumbers=range(1,2)
        results = {}        
        for num in rigNumbers:
            self.ID = num
            tmp=self.GetVersionInformationString()            
            if tmp!="No response" :              
                results[num] = tmp              
            time.sleep(0.10)                      
        return results
    def SendStageProgram(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x02
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendStopProgram(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x03
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()            
    def SendClearProgram(self):
        ba = bytearray(4)
        ba[0]=3        
        ba[1]=self.ID
        ba[2]=0x04
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendSaveProgram(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x05
        ba[3]=self.endByte        
        self.thePort.WriteByteArray(ba)             
        tmp = self.SeekAcknowledgment(30)        
        return tmp
    def SendClearErrors(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x0E
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendLoadProgram(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x06
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment(10)
    def SendUpdateProgram(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x0C
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def GetVersionInformationString(self):
        self.thePort.ClearInputBuffer()
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x07
        ba[3]=self.endByte
        tmp = self.thePort.GetTimeOut() 
        self.thePort.SetTimeOut(0.05)
        self.thePort.WriteByteArray(ba)
        result = self.thePort.ReadCOBSPacket(10)             
        self.thePort.SetTimeOut(tmp)   
        if(len(result)==0):
            return "No response"
        else:
            return result.decode()   
    def UpdateRemoteProgramStatus(self):
        ba = bytearray(4)   
        ba[0]=3     
        ba[1]=self.ID
        ba[2]=0x09
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)   
        tmp = self.thePort.GetTimeOut() 
        self.thePort.SetTimeOut(0.1)      
        result = self.thePort.ReadCOBSPacket(50)          
        decodedResult = cobs.decode(result)  
        self.thePort.SetTimeOut(tmp)        
        if (len(decodedResult)!=38):
            return False      
        if(decodedResult[0]!=0xFE):
            return False  
        decodedResult2 = decodedResult[1:]                   
        self.remoteProgram.FillProgramStatus(decodedResult2)          
        return True    
    def UpdateRemoteProgramData(self):
        ba = bytearray(4)        
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x01
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba) 
        tmp = self.thePort.GetTimeOut() 
        self.thePort.SetTimeOut(20)
        result = self.thePort.ReadCOBSPacket(30000)    
        decodedResult = cobs.decode(result) 
        self.thePort.SetTimeOut(tmp)
        if (len(decodedResult)==0):
            return False      
        if(decodedResult[0]!=0xFE):
            return False  
        decodedResult2 = decodedResult[1:]
        if (len(decodedResult2) % 13 != 0):
            return False
        else:
            self.remoteProgram.FillProgramData(decodedResult2)        
            return True
    def UpdateRemoteProgram(self):
        if self.UpdateRemoteProgramStatus():
            time.sleep(.5)
            return True
            #if self.UpdateRemoteProgramData():
            #    return True
            #else:
            #    return False
        else:            
            return False

    def GetRemoteProgramString(self):        
        if self.UpdateRemoteProgram():
            s1 = self.remoteProgram.GetProgramStatusString()
            #s2 = self.remoteProgram.GetProgramDataString()   
            s2="hi"     
            return "\n***Current Remote Program***\n"+ s1 + "\n\n" + s2
        else:
            return "Get program update failed.\n"

    def GetRemoteProgramStringForGUI(self):        
        if self.UpdateRemoteProgram():
            s1 = self.remoteProgram.GetProgramStatusString()
            s2 = self.remoteProgram.GetProgramDataString()        
            return s1 + "\n\n" + s2
        else:
            return "\nGet program update failed.\n"

    def GetLocalProgramString(self):               
        s1 = self.localProgram.GetProgramStatusString()
        s2 = self.localProgram.GetProgramDataString()
        return "\n***Current Local Program***\n"+ s1 + "\n\n" + s2
    def GetRemoteRTCString(self):
        self.thePort.ClearInputBuffer()
        ba = bytearray(4)        
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x08
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)        
        tmp = self.thePort.GetTimeOut() 
        self.thePort.SetTimeOut(0.05)
        result = self.thePort.ReadCOBSPacket(10)            
        decodedResult = cobs.decode(result)         
        self.thePort.SetTimeOut(tmp)
        if len(decodedResult)==0:
            return "No response"
        if decodedResult[0]>5:
            rtcTime = datetime.datetime(decodedResult[0]+2000,decodedResult[1],decodedResult[2],decodedResult[3],decodedResult[4],decodedResult[5]) 
            s = rtcTime.strftime("%B %d, %Y %H:%M:%S")
            return s
        else:
            return "No RTC"

    def UploadLocalProgram(self): 
        maxProgramSteps=2000
        ba = bytearray(13*maxProgramSteps+100)    
        ba[0]=self.ID   
        ba[1]=0x0A     
        if self.localProgram.programType == Program.ProgramType.LINEAR:
            ba[2]=0x01
        elif self.localProgram.programType == Program.ProgramType.LOOPING:
            ba[2]=0x02
        elif self.localProgram.programType == Program.ProgramType.CIRCADIAN:
            ba[2]=0x03
        else:
            ba[2]=0x01
        tmp = self.localProgram.startTime.timetuple()
        ba[3]=tmp[0]-2000
        ba[4]=tmp[1]
        ba[5]=tmp[2]
        ba[6]=tmp[3]
        ba[7]=tmp[4]
        ba[8]=tmp[5]
                
        if len(self.localProgram.fullProgramSteps) > maxProgramSteps:
            maxIndex = maxProgramSteps
            print("Maximum steps exceeded.  Only uploading first 1500.")
        else:
            maxIndex = len(self.localProgram.fullProgramSteps)
        currentbyteindex=9
        for index in range(maxIndex):
            p=self.localProgram.fullProgramSteps[index]
            ba[currentbyteindex]=p.led1Threshold
            ba[currentbyteindex+1]=p.led2Threshold
            ba[currentbyteindex+2]=p.led3Threshold
            ba[currentbyteindex+3]=p.led4Threshold
            tmp = p.frequency.to_bytes(2,byteorder='big')
            ba[currentbyteindex+4]=tmp[0]
            ba[currentbyteindex+5]=tmp[1]
            tmp = p.dutyCycle.to_bytes(2,byteorder='big')
            ba[currentbyteindex+6]=tmp[0]
            ba[currentbyteindex+7]=tmp[1]
            ba[currentbyteindex+8]=p.triggers
            tmp = p.duration.to_bytes(4,byteorder='big')
            ba[currentbyteindex+9]=tmp[0]
            ba[currentbyteindex+10]=tmp[1]
            ba[currentbyteindex+11]=tmp[2]
            ba[currentbyteindex+12]=tmp[3]
            currentbyteindex+=13          

        ba=ba[0:currentbyteindex]     
        encodedba=cobs.encode(ba)        
        barray = bytearray(encodedba)
        barray.append(0x00)                 
        self.thePort.WriteByteArray(barray)       
        if self.SeekAcknowledgment(10):
            return True
        else:
            return False
    def AreLocalAndRemoteProgramsIdentical(self):
        return self.localProgram.IsProgramIdentical(self.remoteProgram)
    def LoadLocalProgram(self,filePath):
        return self.localProgram.LoadLocalProgram(filePath)
    def LoadLocalProgramFromString(self,ss):
        return self.localProgram.LoadLocalProgramFromString(ss)    

    def SeekAcknowledgment(self,timeoutSeconds=0.5):
        try:
            tmp = self.thePort.GetTimeOut()
            self.thePort.SetTimeOut(timeoutSeconds)
            result = self.thePort.ReadCOBSPacket(4)
            decodedResult = cobs.decode(result) 
            self.thePort.SetTimeOut(tmp)
            if len(decodedResult)!=2:
                return False
            elif decodedResult[0] != 0xFE:
                return False
            else:
                self.currentErrors = decodedResult[1]
                return True
        except:
            return False
    def GetCurrentErrorString(self):
        s="\n        ***Current Errors***\n\n"
        if self.currentErrors & 0x01:
            s+="         UART transfer error: True\n"
        else:
            s+="         UART transfer error: False\n"
        if self.currentErrors & 0x02:
            s+="          UART receive error: True\n"
        else:
            s+="          UART receive error: False\n"
        #if self.currentErrors & 0x04:
        #    s+="                   TBD error: True\n"
        #else:
        #    s+="                   TBD error: False\n"
        if self.currentErrors & 0x08:
            s+="     Command not found error: True\n"
        else:
            s+="     Command not found error: False\n"
        if self.currentErrors & 0x10:
            s+="        Too many steps error: True\n"
        else:
            s+="        Too many steps error: False\n"
        if self.currentErrors & 0x20:
            s+="                   I2C error: True\n"
        else:
            s+="                   I2C error: False\n"
        if self.currentErrors & 0x40:
            s+="                   RTC error: True\n"
        else:
            s+="                   RTC error: False\n"
        #if self.currentErrors & 0x80:
        #    s+="                  TBD2 error: True\n"
        #else:
        #    s+="                  TBD2 error: False\n"
        return s
    def GetCurrentErrors(self):
        ba = bytearray(4)
        ba[0]=3
        ba[1]=self.ID
        ba[2]=0x0D
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendRTCSet(self,timeString):        
        try:
            tmp=datetime.datetime.strptime(timeString,"%m/%d/%Y %H:%M:%S")
        except:
            return False
        ba = bytearray(8)        
        ba[0]=self.ID
        ba[1]=0x0F
        ba[2]=tmp.year-2000
        ba[3]=tmp.month
        ba[4]=tmp.day
        ba[5]=tmp.hour
        ba[6]=tmp.minute
        ba[7]=tmp.second
        encodedba=cobs.encode(ba)            
        barray = bytearray(encodedba)
        barray.append(0x00)          
        self.thePort.WriteByteArray(barray)       
        if self.SeekAcknowledgment():
            return True
        else:
            return False
        
        

if __name__=="__main__" :
    theRig = OptoLifespanRig(1)
    theRig.thePort.Open("/dev/ttyUSB0")
    counter=0 
    print(theRig.GetRemoteProgramString())
    time.sleep(1)
    theRig.SendClearProgram()
    time.sleep(1)
    print(theRig.GetRemoteProgramString())
    #print(theRig.GetVersionInformationString())
    #p=theRig.PrintRemoteProgram()
    #print(p)
    

   


        

    
        
        