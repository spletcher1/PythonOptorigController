from enum import Enum
import datetime

class ProgramType(Enum):
    LINEAR=1
    LOOPING=2
    CIRCADIAN=3
    NONE=4

class ProgramStatus(Enum):
    NOTLOADED=1
    LOADED=2
    STAGED=3
    RUNNING=4
    NONE=5

class ProgramStep:
    def __init__(self):
        self.stepNumber=0
        self.lightsOn=0
        self.frequency=40
        self.pulseWidth=8
        self.duration=60
        self.elapsedDurationAtEnd=datetime.timedelta(0)
        self.time=datetime.timedelta(seconds=self.duration)
    def CopyProgramStep(self,p):
        self.lightsOn = p.lightsOn
        self.frequency = p.frequency
        self.pulseWidth = p.pulseWidth
        self.duration = p.duration
        self.elapsedDurationAtEnd=datetime.timedelta(0)
        self.time=datetime.timedelta(seconds=self.duration)
    def CopyProgramStepFromString(self,p):
        theSplit = p.split(',')
        if len(theSplit) == 4:
            self.lightsOn = int(p[0])
            self.frequency = int(p[1])
            self.pulseWidth = int(p[2])
            self.duration = int(p[3])
            self.elapsedDurationAtEnd=datetime.timedelta(0)
            self.time=datetime.timedelta(seconds=self.duration)
    def GetProgramStepString(self):
        s = 'Step = {:>3d}  Lights = {:>1d}  Freq = {:>3d}  Pulse = {:>3d}  Duration = {:>5d}  Elapsed = {:>5.0f}'.format(self.stepNumber,self.lightsOn,self.frequency,self.pulseWidth,self.duration,self.elapsedDurationAtEnd.total_seconds())
        return s
    def GetProgramStepArrayForUART(self):
        s= str(self.lightsOn) + "," + str(self.frequency) + "," +str(self.pulseWidth) + "," + str(self.duration) +",A"
        if len(s)<11 :
            s= "0"+str(self.lightsOn) + ",0" + str(self.frequency) + "," +str(self.pulseWidth) + "," + str(self.duration) +",A"
        return bytearray(s.encode())
        

   


class Program:
    def __init__(self):
        self.programType = ProgramType.NONE
        self.programStatus = ProgramStatus.NONE
        self.totalProgramDuration=0
        self.elapsedSeconds=0
        self.correctedSeconds=0
        self.numSteps=0
        self.currentStep=0
        self.uninterruptedLoops=0
        self.startTime = datetime.datetime(1,1,1)
        self.rtcTime = datetime.datetime(1,1,1)
        self.fullProgramSteps = []
        self.blockProgramSteps = []
    def ClearProgram(self):
        self.fullProgramSteps.clear()
        self.blockProgramSteps.clear()
        self.programType = ProgramType.NONE
        self.programStatus = ProgramStatus.NONE
        self.startTime = datetime.datetime(1,1,1)
        self.totalProgramDuration = 0
        
    def GetProgramStatusString(self):
        s="\n Program Type: "        
        if self.programType == ProgramType.LINEAR:
            s+="Linear"
        elif self.programType==ProgramType.LOOPING:
            s+="Looping"
        elif self.programType==ProgramType.CIRCADIAN:
            s+="Circadian"
        else:
            s+="Unknown type"

        s+="\nProgram State: "
        if self.programStatus == ProgramStatus.NOTLOADED:
            s+="Not loaded"
        elif self.programStatus==ProgramStatus.LOADED:
            s+="Loaded"
        elif self.programStatus==ProgramStatus.STAGED:
            s+="Staged"
        elif self.programStatus==ProgramStatus.RUNNING:
            s+="Running"
        else:
            s+="Unknown state"

        s+="\n\n            RTC Time: " + self.rtcTime.strftime("%A, %B %d, %Y %H:%M:%S")
        s+="\n          Start Time: " + self.startTime.strftime("%A, %B %d, %Y %H:%M:%S")
        s+="\n\n    Program Duration: " + str(self.totalProgramDuration)
        s+="\n     Elapsed seconds: " + str(self.elapsedSeconds)
        s+="\n  In program seconds: " + str(self.correctedSeconds)
        s+="\n Uninterrupted loops: " + str(self.uninterruptedLoops)
        s+="\n\n Total program steps: " + str(self.numSteps)
        s+="\nCurrent program step: " + str(self.currentStep)
        return s
    def GetProgramDataString(self):
        s=""
        for i in range(self.numSteps):
            s+=self.fullProgramSteps[i].GetProgramStepString() +"\n"
        return s
    def FillProgramStatus(self,bytesData):
        if bytesData[0]==1:
            self.programStatus = ProgramStatus.NOTLOADED
        elif bytesData[0]==2:
            self.programStatus = ProgramStatus.LOADED
        elif bytesData[0]==3:
            self.programStatus = ProgramStatus.STAGED
        elif bytesData[0]==4:
            self.programStatus = ProgramStatus.RUNNING
        else:
            self.programStatus = ProgramStatus.NONE           

        if bytesData[1]==1:
            self.programType = ProgramType.LINEAR
        elif bytesData[1]==2:
            self.programType = ProgramType.LOOPING
        elif bytesData[1]==3:
            self.programType = ProgramType.CIRCADIAN
        else:
            self.programType = ProgramType.NONE

        if(bytesData[2]+bytesData[3]+bytesData[4]+bytesData[5]+bytesData[6]+bytesData[7]==0):
            self.startTime = datetime.datetime(1,1,1)
        else:
            self.startTime = datetime.datetime(bytesData[2]+2000,bytesData[3],bytesData[4],bytesData[5],bytesData[6],bytesData[7])        
        
        if(bytesData[8]+bytesData[9]+bytesData[10]+bytesData[11]+bytesData[12]+bytesData[13]==0):
            self.rtcTime = datetime.datetime(1,1,1)
        else:
            self.rtcTime = datetime.datetime(bytesData[8]+2000,bytesData[9],bytesData[10],bytesData[11],bytesData[12],bytesData[13])    

        self.elapsedSeconds = bytesData[14]<<24    
        self.elapsedSeconds += bytesData[15]<<16    
        self.elapsedSeconds += bytesData[16]<<8    
        self.elapsedSeconds += bytesData[17]    

        self.correctedSeconds = bytesData[18]<<24    
        self.correctedSeconds += bytesData[19]<<16    
        self.correctedSeconds += bytesData[20]<<8    
        self.correctedSeconds += bytesData[21]   

        self.totalProgramDuration = bytesData[22]<<24    
        self.totalProgramDuration += bytesData[23]<<16    
        self.totalProgramDuration += bytesData[24]<<8    
        self.totalProgramDuration += bytesData[25]    

        self.numSteps = bytesData[26]<<8    
        self.numSteps += bytesData[27]    
        self.currentStep = bytesData[28]<<8    
        self.currentStep += bytesData[29]+1  

        self.uninterruptedLoops = bytesData[30]<<24    
        self.uninterruptedLoops += bytesData[31]<<16    
        self.uninterruptedLoops += bytesData[32]<<8    
        self.uninterruptedLoops += bytesData[33]   
    def FillInElapsedTimes(self):
        if len(self.fullProgramSteps)<1:
            return
        self.fullProgramSteps[0].elapsedDurationAtEnd = self.fullProgramSteps[0].time
        for i in range(1,len(self.fullProgramSteps)):
            self.fullProgramSteps[i].elapsedDurationAtEnd = self.fullProgramSteps[i-1].elapsedDurationAtEnd + self.fullProgramSteps[i].time
        self.totalProgramDuration = self.fullProgramSteps[len(self.fullProgramSteps)-1].elapsedDurationAtEnd.total_seconds()
        self.numSteps = len(self.fullProgramSteps)
    def FillProgramData(self, bytesData):
        theSplit = str(bytesData).split(',')
        numsteps = (int)((len(theSplit)-2)/5)
        if numsteps < 1:
            return
        self.fullProgramSteps.clear()
        for i in range(numsteps):
            tmp = ProgramStep()
            tmp.stepNumber = i+1
            tmp.lightsOn = int(theSplit[i*5+2])
            tmp.frequency = int(theSplit[i*5+3])
            tmp.pulseWidth = int(theSplit[i*5+4])
            tmp.duration = int(theSplit[i*5+5])
            tmp.time = datetime.timedelta(seconds=tmp.duration)
            tmp.elapsedDurationAtEnd = datetime.timedelta(0)
            self.fullProgramSteps.append(tmp)
        self.FillInElapsedTimes()      
    def LoadLocalProgram(self,filePath):
        isInBlock = False
        totalBlockIterations=1
        tmp=""

        readFile = open(filePath,'r')
        program=readFile.readlines()
        print(program)


            
