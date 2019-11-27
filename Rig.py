import time
import _thread 
import socketserver 
import MyUART
import Program

class OptoLifespanRig:
    def __init__(self, ID):
        self.ID = ID
        self.thePort=MyUART.MyUART()
        self.startByte=0x40 
        self.endByte=0x41   #'A'#'@'
        self.remoteProgram = Program.Program()
        self.localProgram = Program.Program()
    def SendStageProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x02
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendStopProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x03
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendClearProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x04
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendSaveProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x05
        ba[3]=self.endByte
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
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x06
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
    def SendUpdateProgram(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x0C
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba)
    def GetVersionInformation(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x07
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(50)
        return f'Firmware Version: {result.decode()}'
    def UpdateRemoteProgramStatus(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x09
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(34)
        self.remoteProgram.FillProgramStatus(result)       
    def UpdateRemoteProgramData(self):
        ba = bytearray(4)
        ba[0]=self.startByte
        ba[1]=self.ID
        ba[2]=0x01
        ba[3]=self.endByte
        self.thePort.WriteByteArray(ba) 
        result = self.thePort.Read(3000)
        if len(result)==0:
            return "No response"
        if result[0]==self.startByte and result[len(result)-1]==self.endByte:
            self.remoteProgram.FillProgramData(result)
        else:
            print("No response")
    def PrintRemoteProgram(self):
        self.UpdateRemoteProgramData()
        self.UpdateRemoteProgramStatus()
        s1 = self.remoteProgram.GetProgramStatusString()
        s2 = self.remoteProgram.GetProgramDataString()
        return "\n***Current Remote Program***\n"+ s1 + "\n\n" + s2

            
        

if __name__=="__main__" :
    theRig = OptoLifespanRig(14)
    p=theRig.PrintRemoteProgram()
    print(p)
    

   


        

    
        
        