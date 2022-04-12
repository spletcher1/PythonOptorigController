from enum import Enum
import datetime
import sys

class ProgramGroup:
    def __init__(self):
        self.groupNumber=0
        self.groupDurationSeconds=60
        self.numSteps=0
        self.programSteps = []
        self.numIterations=0
        self.elapsedSecondsAtStart=0
        self.iterationDurationSeconds=0
        self.elapsedSecondsAtEnd=0
        self.time=datetime.timedelta(seconds=self.groupDurationSeconds)
        self.currentStep=0

    def IsGroupIdentical(self, g):
        if(self.groupDurationSeconds!=g.groupDurationSeconds): return False
        if(self.numSteps!=g.numSteps): return False
        if(self.numIterations!=g.numIterations): return False
        for i in range(len(self.programSteps)):
            if(self.programSteps[i].IsStepIdentical(g.programSteps[i]) == False) : return False
        return True

    def AddStep(self,step,isProgramLocal):     
        step.stepNumber=self.numSteps   
        self.programSteps.append(step)
        self.numSteps+=1
        self.UpdateTimes(isProgramLocal)

    def GetProgramGroupString(self):
        s='*** Starting at {:d} seconds\n'.format(self.elapsedSecondsAtStart)
        s+= 'Group = {:<3d}  Iterations = {:<5d}  I_Duration = {:<5d}  G_Duration = {:<5d}  Elapsed = {:<5d} '.format(self.groupNumber,self.numIterations,self.iterationDurationSeconds,self.groupDurationSeconds,self.elapsedSecondsAtEnd) + "\n"
        if(self.numSteps<1):
            s+= "So steps defined.\n"
        else:
            for i in range(self.numSteps):
                s+=self.programSteps[i].GetProgramStepString() +"\n"
        return s

    def UpdateTimes(self,isProgramLocal):
        if(isProgramLocal):
            self.UpdateTimesLocal()
        else:
            self.UpdateTimesRemote()

    def UpdateTimesLocal(self):        
        if(self.numSteps<1):
            self.groupDurationSeconds=0
            self.iterationDurationSeconds=0
            return
        tmpDuration=0
        self.programSteps[0].elapsedSecondsAtEnd = self.programSteps[0].time.total_seconds()
        tmpDuration+=self.programSteps[0].duration
        for i in range(1,len(self.programSteps)):                       
            self.programSteps[i].elapsedSecondsAtEnd = self.programSteps[i-1].elapsedSecondsAtEnd + self.programSteps[i].time.total_seconds()
            tmpDuration+=self.programSteps[i].duration
        self.iterationDurationSeconds=int(tmpDuration)
        self.groupDurationSeconds = self.iterationDurationSeconds*self.numIterations     
        self.time=datetime.timedelta(seconds=self.groupDurationSeconds)   

    def UpdateTimesRemote(self):
        self.time=datetime.timedelta(seconds=self.groupDurationSeconds)   
        return

    def GetProgramGroupArrayForUART(self):
        return " "
