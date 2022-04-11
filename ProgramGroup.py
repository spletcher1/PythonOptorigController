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
        self.elapsedSecondsAtEnd=datetime.timedelta(0)
        self.time=datetime.timedelta(seconds=self.groupDurationSeconds)
        self.currentStep=0

    def IsGroupIdentical(self, g):
        if(self.groupDurationSeconds!=g.groupDurationSeconds): return False
        if(self.numSteps!=g.numSteps): return False
        if(self.numIterations!=g.numIterations): return False
        for i in range(len(self.programSteps)):
            if(self.programSteps[i].IsStepIdentical(g.programSteps[i]) == False) : return False
        return True

    def AddStep(self,step):
        self.programSteps.append(step)
        self.numSteps+=1

    def GetProgramGroupString(self):
        s="***\n"
        s+= 'Group = {:>3d}  Iterations = {:>5d}  Duration = {:>5d}  Elapsed = {:>5.0f} '.format(self.groupNumber,self.numIterations,self.groupDurationSeconds,self.elapsedSecondsAtEnd.total_seconds()) + "\n"
        if(self.numSteps<1):
            s+= "So steps defined.\n"
        else:
            for i in range(self.numSteps):
                s+=self.programSteps[i].GetProgramStepString() +"\n"
        return s


    def GetProgramGroupArrayForUART(self):
        return " "
