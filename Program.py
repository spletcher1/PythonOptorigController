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
    LOCAL=5
    NONE=6

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
        self.stepNumber = p.stepNumber
    def CopyProgramStepFromString(self,p):
        theSplit = p.split(',')
        if len(theSplit) == 4:
            self.lightsOn = int(theSplit[0])
            self.frequency = int(theSplit[1])
            self.pulseWidth = int(theSplit[2])
            self.duration = int(theSplit[3])
            self.elapsedDurationAtEnd=datetime.timedelta(0)
            self.time=datetime.timedelta(seconds=self.duration)
            self.stepNumber = 0
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
        self.startTime = datetime.datetime(2001,1,1)
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
        elif self.programStatus==ProgramStatus.LOCAL:
            s+="Local program"
        else:
            s+="Unknown state"

        if self.programStatus != ProgramStatus.LOCAL:
            s+="\n\n            RTC Time: " + self.rtcTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+="\n          Start Time: " + self.startTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+="\n\n    Program Duration: " + str(self.totalProgramDuration)
            s+="\n     Elapsed seconds: " + str(self.elapsedSeconds)
            s+="\n  In program seconds: " + str(self.correctedSeconds)
            s+="\n Uninterrupted loops: " + str(self.uninterruptedLoops)
            s+="\n\n Total program steps: " + str(self.numSteps) + "\n"
            s+="\nCurrent program step: " + str(self.currentStep)
        else:
            s+="\n\n          Start Time: " + self.startTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+="\n\n    Program Duration: " + str(self.totalProgramDuration)           
            s+="\n\n Total program steps: " + str(self.numSteps) + "\n"           
        return s
    def GetProgramDataString(self):
        s=""
        if self.numSteps < 1: return s
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
        numsteps = (int)(len(bytesData)/9)
        if numsteps < 1:
            return
        self.fullProgramSteps.clear()
        indexer=0
        for i in range(numsteps):           
            tmp = ProgramStep()
            tmp.stepNumber = i+1
            tmp.lightsOn = int(bytesData[indexer])
            tmp.frequency = int(bytesData[indexer+1]<<8) + int(bytesData[indexer+2])
            tmp.pulseWidth = int(bytesData[indexer+3]<<8) + int(bytesData[indexer+4])
            tmp.duration = int(bytesData[indexer+5]<<24) + int(bytesData[indexer+6]<<16) + int(bytesData[indexer+7]<<8) +int(bytesData[indexer+8])
            tmp.time = datetime.timedelta(seconds=tmp.duration)
            tmp.elapsedDurationAtEnd = datetime.timedelta(0)
            self.fullProgramSteps.append(tmp)
            indexer+=9
        self.FillInElapsedTimes()      
    def LoadLocalProgram(self,filePath):
        isInBlock = False
        totalBlockIterations=1
        tmp=""
        readFile = open(filePath,'r')
        program=readFile.readlines()
        readFile.close()
        self.ClearProgram()
        for i in range(len(program)):
            aline = program[i].strip()
            if aline[0]=='#':
                continue
            if aline[0]=='[' and aline.find(']') != -1:
                index = aline.find(']')     
                tmp=aline[1:index]       
                if tmp.lower() == 'beginblock':
                    isInBlock=True
                    totalBlockIterations=1
                    self.blockProgramSteps.clear()
                elif tmp.lower() == 'endblock':
                    isInBlock=False
                    for ii in range(totalBlockIterations):
                        for jj in range(len(self.blockProgramSteps)):
                            pp = ProgramStep()
                            pp.CopyProgramStep(self.blockProgramSteps[jj])                            
                            pp.stepNumber = len(self.fullProgramSteps)+1
                            self.fullProgramSteps.append(pp)
            else:
                theSplit = aline.split(':')              
                if len(theSplit) > 2:
                    theSplit[1] += ':' + theSplit[2] + ':' + theSplit[3]
                if len(theSplit) >= 2:
                    if theSplit[0].lower() == 'iterations':
                        if isInBlock == True:
                            totalBlockIterations = int(theSplit[1].strip())
                    elif theSplit[0].lower() == 'interval':
                        p = ProgramStep()
                        p.CopyProgramStepFromString(theSplit[1])
                        if isInBlock == True:
                            self.blockProgramSteps.append(p)
                        else:
                            p.stepNumber = len(self.fullProgramSteps)+1
                            self.fullProgramSteps.append(p)
                    elif theSplit[0].lower() == 'starttime':
                        tmp = theSplit[1].strip()
                        if tmp.find('/') != -1:
                            self.startTime = datetime.datetime.strptime(tmp,"%m/%d/%Y %H:%M:%S")
                        else:
                            tmp2 = datetime.datetime.strptime(tmp,"%H:%M:%S")
                            tmp2 = tmp2.time()
                            tmp3 = datetime.date.today()
                            self.startTime = datetime.datetime.combine(tmp3,tmp2)
                    elif theSplit[0].lower() == 'programtype':
                        ss = theSplit[1].strip()
                        if ss.lower() == 'linear':
                            self.programType = ProgramType.LINEAR
                        elif ss.lower()== 'looping':
                            self.programType = ProgramType.LOOPING
                        elif ss.lower() == 'circadian':
                            self.programType = ProgramType.CIRCADIAN
                        else:
                            self.programType = ProgramType.LOOPING
        self.programStatus = ProgramStatus.LOCAL   
        self.FillInElapsedTimes()
    def IsProgramIdentical(self, p):
        if self.programType != p.programType: return False
        if self.startTime != p.startTime: return False
        if len(self.fullProgramSteps) != len(p.fullProgramSteps): return False
        for i in range(len(self.fullProgramSteps)):
            if self.fullProgramSteps[i].lightsOn != p.fullProgramSteps[i].lightsOn: return False 
            if self.fullProgramSteps[i].frequency != p.fullProgramSteps[i].frequency: return False
            if self.fullProgramSteps[i].pulseWidth != p.fullProgramSteps[i].pulseWidth: return False
            if self.fullProgramSteps[i].duration != p.fullProgramSteps[i].duration: return False
        return True





            
