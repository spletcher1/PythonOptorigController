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
    def GetListOfOnlineRigs(self):
        rigNumbers=range(1,20)
        results = {}
        self.thePort.SetShortTimeout()
        for num in rigNumbers:
            self.ID = num
            tmp=self.GetVersionInformationString()
            if tmp!="No response" :
                results[num] = tmp
        self.thePort.ResetTimeout()
        return results
    def SendStageProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x02
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendStopProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x03
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()            
    def SendClearProgram(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x04
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendSaveProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x05
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendClearErrors(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x0E
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendLoadProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x06
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def SendUpdateProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x0C
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()
    def GetVersionInformationString(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x07
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(5)
        if(len(result)==0):
            return "No response"
        else:
            return result.decode()
    def UpdateRemoteProgramStatus(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x09
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)         
        result = self.thePort.ReadCOBSPacket(50)   
        decodedResult = cobs.decode(result)  
        if (len(decodedResult)!=35):
            return False      
        if(decodedResult[0]!=0xFE):
            return False  
        decodedResult2 = decodedResult[1:]           
        self.remoteProgram.FillProgramStatus(decodedResult2)          
        return True    
    def UpdateRemoteProgramData(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x01
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.ReadCOBSPacket(3000)    
        decodedResult = cobs.decode(result) 
        if (len(decodedResult)==0):
            return False      
        if(decodedResult[0]!=0xFE):
            return False  
        decodedResult2 = decodedResult[1:]
        if (len(decodedResult2) % 9 != 0):
            return False
        else:
            self.remoteProgram.FillProgramData(decodedResult2)        
            return True
    def UpdateRemoteProgram(self):
        if self.UpdateRemoteProgramStatus():
            time.sleep(.5)
            if self.UpdateRemoteProgramData():
                return True
            else:
                return False
        else:
            return False

    def GetRemoteProgramString(self):        
        if self.UpdateRemoteProgram():
            s1 = self.remoteProgram.GetProgramStatusString()
            s2 = self.remoteProgram.GetProgramDataString()        
            return "\n***Current Remote Program***\n"+ s1 + "\n\n" + s2
        else:
            return "\nGet program update failed.\n"
    def GetLocalProgramString(self):               
        s1 = self.localProgram.GetProgramStatusString()
        s2 = self.localProgram.GetProgramDataString()
        return "\n***Current Local Program***\n"+ s1 + "\n\n" + s2
    def GetRemoteRTCString(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x08
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(6)    
        if len(result)==0:
            return "No response"
        if result[0]>5:
            rtcTime = datetime.datetime(result[0]+2000,result[1],result[2],result[3],result[4],result[5]) 
            s = "Local time on RTC: {}".format(rtcTime.strftime("%A, %B %d, %Y %H:%M:%S"))
            return s
        else:
            return "No RTC"
    def UploadLocalProgram(self):
        maxProgramSteps=40
        ba = bytearray(9*maxProgramSteps+9)    
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
            print("Maximum steps exceeded.  Only uploading first 40.")
        else:
            maxIndex = len(self.localProgram.fullProgramSteps)
        currentbyteindex=9
        for index in range(maxIndex):
            p=self.localProgram.fullProgramSteps[index]
            ba[currentbyteindex]=p.lightsOn
            tmp = p.frequency.to_bytes(2,byteorder='big')
            ba[currentbyteindex+1]=tmp[0]
            ba[currentbyteindex+2]=tmp[1]
            tmp = p.pulseWidth.to_bytes(2,byteorder='big')
            ba[currentbyteindex+3]=tmp[0]
            ba[currentbyteindex+4]=tmp[1]
            tmp = p.duration.to_bytes(4,byteorder='big')
            ba[currentbyteindex+5]=tmp[0]
            ba[currentbyteindex+6]=tmp[1]
            ba[currentbyteindex+7]=tmp[2]
            ba[currentbyteindex+8]=tmp[3]
            currentbyteindex+=9          

        ba=ba[0:currentbyteindex]     
        encodedba=cobs.encode(ba)        
        barray = bytearray(encodedba)
        barray.append(0x00)          
        print("Length")
        print(len(barray))
        self.thePort.WriteByteArray(barray)       
        if self.SeekAcknowledgment():
            return True
        else:
            return False
    def AreLocalAndRemoteProgramsIdentical(self):
        return self.localProgram.IsProgramIdentical(self.remoteProgram)
    def LoadLocalProgram(self,filePath):
        self.localProgram.LoadLocalProgram(filePath)
    def SeekAcknowledgment(self):
        result = self.thePort.Read(3)
        if len(result)!=3:
            return False
        elif result[0] != 0xFE:
            return False
        else:
            self.currentErrors = result[1]
            return True
    def GetCurrentErrorString(self):
        s="\n        ***Current Errors***\n\n"
        if self.currentErrors & 0x01:
            s+="            UART frame error: True\n"
        else:
            s+="            UART frame error: False\n"
        if self.currentErrors & 0x02:
            s+="  UART buffer overflow error: True\n"
        else:
            s+="  UART buffer overflow error: False\n"
        if self.currentErrors & 0x04:
            s+="UART register overflow error: True\n"
        else:
            s+="UART register overflow error: False\n"
        if self.currentErrors & 0x08:
            s+="     Command not found error: True\n"
        else:
            s+="     Command not found error: False\n"
        if self.currentErrors & 0x10:
            s+="        Too many steps error: True\n"
        else:
            s+="        Too many steps error: False\n"
        if self.currentErrors & 0x20:
            s+="           I2C timeout error: True\n"
        else:
            s+="           I2C timeout error: False\n"
        if self.currentErrors & 0x40:
            s+="                   Bitflag 1: True\n"
        else:
            s+="                   Bitflag 1: False\n"
        if self.currentErrors & 0x40:
            s+="                   Bitflag 2: True\n"
        else:
            s+="                   Bitflag 2: False\n"
        return s
    def GetCurrentErrors(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x0D
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        return self.SeekAcknowledgment()

if __name__=="__main__" :
    theRig = OptoLifespanRig(14)    
    #p=theRig.PrintRemoteProgram()
    #print(p)
    

   


        

    
        
        