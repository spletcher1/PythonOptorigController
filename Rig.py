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
    def GetListOfOnlineRigs(self):
        rigNumbers=range(1,20)
        results = {}
        for num in rigNumbers:
            self.ID = num
            tmp=self.GetVersionInformationString()
            if tmp!="No response" :
                results[num] = tmp
        return results
    def SendStageProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x02
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def SendStopProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x03
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def SendClearProgram(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x04
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def SendSaveProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x05
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def SendLoadProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x06
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def SendUpdateProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x0C
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            return True
    def GetVersionInformationString(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x07
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(50)
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
        self.remoteProgram.FillProgramStatus(decodedResult)       
    def UpdateRemoteProgramData(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x01
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.ReadCOBSPacket(3000)
        decodedResult = cobs.decode(result)        
        if (len(decodedResult)==0) or (len(decodedResult) % 9 != 0):
            return "No response"
        self.remoteProgram.FillProgramData(decodedResult)        
    def UpdateRemoteProgram(self):
        self.UpdateRemoteProgramData()
        time.sleep(.5)
        self.UpdateRemoteProgramStatus() 
    def GetRemoteProgramString(self):        
        self.UpdateRemoteProgramData()
        s1 = self.remoteProgram.GetProgramStatusString()
        s2 = self.remoteProgram.GetProgramDataString()        
        return "\n***Current Remote Program***\n"+ s1 + "\n\n" + s2
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
        if sum(result)>0:
            rtcTime = datetime.datetime(result[0]+2000,result[1],result[2],result[3],result[4],result[5]) 
            s = "Local time on RTC: {}".format(rtcTime.strftime("%A, %B %d, %Y %H:%M:%S"))
            return s
        else:
            return "No RTC"
    def SendProgramStep(self,programStep):
        tmp = programStep.GetProgramStepArrayForUART()        
        ba = bytearray(len(tmp)+2)
        ba[0]=self.startByte
        ba[1]=self.ID
        for index in range(len(tmp)):
            ba[index+2]=tmp[index]
        self.thePort.WriteByteArray(ba)
    def UploadLocalProgram(self):
        ba = bytearray(256)    
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
        
        maxProgramSteps=20
        if len(self.localProgram.fullProgramSteps) > maxProgramSteps:
            maxIndex = maxProgramSteps
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
        print(len(ba))
        encodedba=encodedba+b'0'
        self.thePort.WriteByteArray(ba)
        result = self.thePort.Read(1)
        if len(result)!=1:
            return False
        elif result[0] != 0xFF:
            return False
        else:
            time.sleep(1)
            self.SendUpdateProgram() 
            result = self.thePort.Read(1)
            if len(result)!=1:
                return False
            elif result[0] != 0xFF:
                return False
            else:
                return True
              
    def AreLocalAndRemoteProgramsIdentical(self):
        return self.localProgram.IsProgramIdentical(self.remoteProgram)
    def LoadLocalProgram(self,filePath):
        self.localProgram.LoadLocalProgram(filePath)


if __name__=="__main__" :
    theRig = OptoLifespanRig(14)    
    #p=theRig.PrintRemoteProgram()
    #print(p)
    

   


        

    
        
        