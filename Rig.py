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
    def SendStopProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x03
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendClearProgram(self):
        ba = bytearray(3)        
        ba[0]=self.ID
        ba[1]=0x04
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendSaveProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x05
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendProgramType(self,programType):
        ba = bytearray(5)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x0A
        if programType == Program.ProgramType.LINEAR:
            ba[3]=0x01
        elif programType == Program.ProgramType.LOOPING:
            ba[3]=0x02
        elif programType == Program.ProgramType.CIRCADIAN:
            ba[3]=0x03
        else:
            ba[3]=0x01
        ba[4]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendProgramStartTime(self,startTime):
        ba=bytearray(10)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x0B
        tmp = startTime.timetuple()
        ba[3]=tmp[0]-2000
        ba[4]=tmp[1]
        ba[5]=tmp[2]
        ba[6]=tmp[3]
        ba[7]=tmp[4]
        ba[8]=tmp[5]
        ba[9]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendLoadProgram(self):
        ba = bytearray(3)
        ba[0]=self.ID
        ba[1]=0x06
        ba[2]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendUpdateProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x0C
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
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
        self.SendClearProgram()
        time.sleep(0.1)
        ba = bytearray(5)    
        ba[0]=self.ID        
        if self.localProgram.programType == Program.ProgramType.LINEAR:
            ba[1]=0x01
        elif self.localProgram.programType == Program.ProgramType.LOOPING:
            ba[1]=0x02
        elif self.localProgram.programType == Program.ProgramType.CIRCADIAN:
            ba[1]=0x03
        else:
            ba[1]=0x01
        tmp = self.localProgram.startTime.timetuple()
        ba[2]=tmp[0]-2000
        ba[3]=tmp[1]
        ba[4]=tmp[2]
        ba[5]=tmp[3]
        ba[6]=tmp[4]
        ba[7]=tmp[5]
        
        maxProgramSteps=20
        if len(self.localProgram.fullProgramSteps) > maxProgramSteps:
            maxIndex = maxProgramSteps
        else:
            maxIndex = len(self.localProgram.fullProgramSteps)
        for index in range(maxIndex):
                                  
        
        time.sleep(.5)
        self.SendUpdateProgram()        
    def AreLocalAndRemoteProgramsIdentical(self):
        return self.localProgram.IsProgramIdentical(self.remoteProgram)
    def LoadLocalProgram(self,filePath):
        self.localProgram.LoadLocalProgram(filePath)


if __name__=="__main__" :
    theRig = OptoLifespanRig(14)    
    #p=theRig.PrintRemoteProgram()
    #print(p)
    

   


        

    
        
        