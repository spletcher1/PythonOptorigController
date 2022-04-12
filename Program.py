from enum import Enum
import datetime
import sys
from ProgramStep import ProgramStep
from ProgramGroup import ProgramGroup

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

class Program:
    def __init__(self):
        self.programType = ProgramType.NONE
        self.programStatus = ProgramStatus.NONE
        self.totalProgramDuration=0
        self.elapsedSeconds=0
        self.correctedSeconds=0
        self.uninterruptedLoops=0
        self.startTime = datetime.datetime(1,1,1)
        self.rtcTime = datetime.datetime(1,1,1)
        self.numGroups=0
        self.currentGroupNumber=-1
        self.currentIteration=0       
        self.programGroups = []

    def ClearProgram(self):
        self.programGroups.clear()
        self.programType = ProgramType.NONE
        self.programStatus = ProgramStatus.NONE
        self.startTime = datetime.datetime(2001,1,1)
        self.totalProgramDuration = 0
        self.elapsedSeconds=0
        self.correctedSeconds=0
        self.uninterruptedLoops=0
        self.numGroups=0
        self.currentGroupNumber=0
        self.currentIteration=0       
        
    
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
            s+="\n\n             RTC Time: " + self.rtcTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+=  "\n           Start Time: " + self.startTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+="\n\n     Program Duration: " + str(self.totalProgramDuration)
            s+=  "\n      Elapsed seconds: " + str(self.elapsedSeconds)
            s+=  "\n   In program seconds: " + str(self.correctedSeconds)
            s+=  "\n  Uninterrupted loops: " + str(self.uninterruptedLoops)
            s+="\n\n Total program groups: " + str(self.numGroups) + "\n"
        else:
            s+="\n\n           Start Time: " + self.startTime.strftime("%A, %B %d, %Y %H:%M:%S")
            s+="\n\n     Program Duration: " + str(self.totalProgramDuration)           
            s+="\n\n Total program groups: " + str(self.numGroups) + "\n"           
        return s

    def GetProgramDataString(self):
        s=""        
        if self.numGroups < 1:
            s = "No program groups defined.\n\n"
            return s
        else:
            for i in range(self.numGroups):
                s+=self.programGroups[i].GetProgramGroupString() +"\n"
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

        self.numGroups=bytesData[26]
        self.currentGroupNumber=bytesData[27]

        self.currentIteration = bytesData[28]<<24    
        self.currentIteration += bytesData[29]<<16    
        self.currentIteration += bytesData[30]<<8    
        self.currentIteration += bytesData[31] 
        
        self.numSteps += bytesData[32]    
        
        self.uninterruptedLoops = bytesData[33]<<24    
        self.uninterruptedLoops += bytesData[34]<<16    
        self.uninterruptedLoops += bytesData[35]<<8    
        self.uninterruptedLoops += bytesData[36] 

    def FillProgramData(self, bytesData):
        self.programGroups.clear()         
        if len(bytesData) < 10:
            return  
        indexer=0
        self.numGroups = int(bytesData[indexer])
        for j in range(self.numGroups):
            tmp = ProgramGroup()
            tmp.groupNumber=int(bytesData[indexer+1])
            tmp.numIterations = int(bytesData[indexer+2]<<24) + int(bytesData[indexer+3]<<16) + int(bytesData[indexer+4]<<8) +int(bytesData[indexer+5])
            tmp.numSteps = int(bytesData[indexer+6])
            tmp.groupDurationSeconds = int(bytesData[indexer+7]<<24) + int(bytesData[indexer+8]<<16) + int(bytesData[indexer+9]<<8) +int(bytesData[indexer+10])
            tmp.iterationDurationSeconds = int(bytesData[indexer+11]<<24) + int(bytesData[indexer+12]<<16) + int(bytesData[indexer+13]<<8) +int(bytesData[indexer+14])

            for i in range(tmp.numSteps):           
                tmp2 = ProgramStep()
                tmp2.stepNumber = i+1
                tmp2.led1Threshold = int(bytesData[indexer+15])
                tmp2.led2Threshold = int(bytesData[indexer+16])
                tmp2.led3Threshold = int(bytesData[indexer+17])
                tmp2.led4Threshold = int(bytesData[indexer+18])
                tmp2.frequency = int(bytesData[indexer+19]<<8) + int(bytesData[indexer+20])
                tmp2.dutyCycle = int(bytesData[indexer+21])
                tmp2.triggers = int(bytesData[indexer+22])
                tmp2.duration = int(bytesData[indexer+23]<<24) + int(bytesData[indexer+24]<<16) + int(bytesData[indexer+25]<<8) +int(bytesData[indexer+26])
                tmp2.time = datetime.timedelta(seconds=tmp.duration)
                tmp2.elapsedDurationAtEnd = datetime.timedelta(0)
                tmp.programSteps.append(tmp2)
                indexer+=27

            self.programGroups.append(tmp)
        self.FillInElapsedTimes()    

    def FillInElapsedTimes(self):
        if self.numGroups<1:
            self.totalProgramDuration=0
            return             
        self.programGroups[0].elapsedSecondsAtEnd = self.programGroups[0].time        
        for i in range(1,len(self.programGroups)):                 
            self.programGroups[i].elapsedSecondsAtEnd = self.programGroups[i-1].elapsedSecondsAtEnd + self.programGroups[i].time
        self.totalProgramDuration = self.programGroups[len(self.programGroups)-1].elapsedSecondsAtEnd.total_seconds()


    def IsProgramIdentical(self, p):
        if self.programType != p.programType: return False
        if self.startTime != p.startTime: return False
        if len(self.programGroups) != len(p.programGroups): return False
        for j in range(self.numGroups):
            if(self.programGroups[i].IsGroupIdentical(p.programGroups[i])==False): return False
        return True

    def LoadLocalProgram(self,filePath):
        tmp=""
        try:
            readFile = open(filePath,'r')
        except:
            print("\nFile open error. Program not loaded.\n")
            return False    
        try:   
            program=readFile.readlines()
            readFile.close()
            self.ClearProgram()
            for i in range(len(program)):
                aline = program[i].strip()           
                if aline[0]=='#':
                    continue
                else:
                    theSplit = aline.split(':')     
                    if len(theSplit) > 2: # this only happens for the starttime line.  combine the time parts.
                        theSplit[1] += ':' + theSplit[2] + ':' + theSplit[3]
                    if len(theSplit) == 2:
                        if theSplit[0].lower() == 'group':                    
                            pg=ProgramGroup()
                            pg.numIterations=int(theSplit[1].strip())
                            pg.groupNumber = self.numGroups+1
                            self.numGroups+=1
                            self.programGroups.append(pg)       
                        elif theSplit[0].lower() == 'interval':
                            p = ProgramStep()
                            if(p.CopyProgramStepFromString(theSplit[1])==False):
                                return False
                            if(self.numGroups==0):
                                pg=ProgramGroup()
                                pg.numIterations=1
                                pg.groupNumber = self.numGroups+1
                                self.numGroups+=1
                                self.programGroups.append(pg)       
                            self.programGroups[self.numGroups-1].AddStep(p)
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
            return True       
                               
        except:
            print("\nFile load error. Program not loaded.\n")
            return False  
          
    def LoadLocalProgramFromString(self,ss):
        isInBlock = False
        totalBlockIterations=1        
        try:   
            program=ss.splitlines()            
            self.ClearProgram()
            for i in range(len(program)):
                aline = program[i].strip()           
                if aline[0]=='#':
                    continue
                else:
                    theSplit = aline.split(':')     
                    if len(theSplit) > 2: # this only happens for the starttime line.  combine the time parts.
                        theSplit[1] += ':' + theSplit[2] + ':' + theSplit[3]
                    if len(theSplit) == 2:
                        if theSplit[0].lower() == 'group':                    
                            pg=ProgramGroup()
                            pg.numIterations=int(theSplit[1].strip())
                            pg.groupNumber = self.numGroups+1
                            self.numGroups+=1
                            self.programGroups.append(pg)       
                        elif theSplit[0].lower() == 'interval':
                            p = ProgramStep()
                            if(p.CopyProgramStepFromString(theSplit[1])==False):
                                return False
                            if(self.numGroups==0):
                                pg=ProgramGroup()
                                pg.numIterations=1
                                pg.groupNumber = self.numGroups+1
                                self.numGroups+=1
                                self.programGroups.append(pg)       
                            self.programGroups[self.numGroups-1].AddStep(p)
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
            return True     
        except:
            print("\nFile load error. Program not loaded.\n")
            return False   

   

if __name__=="__main__" :
    theProgram = Program()
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    theProgram.LoadLocalProgram(sys.argv[1])
    print(theProgram.GetProgramStatusString())
    print(theProgram.GetProgramDataString())



            
