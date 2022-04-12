from enum import Enum
import datetime
import sys

class ProgramStep:
    def __init__(self):
        self.stepNumber=0
        self.led1Threshold=0
        self.led2Threshold=0
        self.led3Threshold=0
        self.led4Threshold=0
        self.frequency=40
        self.dutyCycle=8
        self.duration=60
        self.triggers=0
        self.elapsedSecondsAtEnd=0
        self.time=datetime.timedelta(seconds=self.duration)

    def IsStepIdentical(self, s):
        if self.led1Threshold != s.led1Threshold: return False 
        if self.led2Threshold != s.led2Threshold: return False 
        if self.led3Threshold != s.led3Threshold: return False 
        if self.led4Threshold != s.led4Threshold: return False 
        if self.frequency != s.frequency: return False
        if self.dutyCycle != s.dutyCycle: return False
        if self.triggers != s.triggers: return False
        if self.duration != s.duration: return False
        if self.elapsedSecondsAtEnd != s.elapsedSecondsAtEnd: return False
        return True
    
    def CopyProgramStep(self,p):
        self.led1Threshold = p.led1Threshold
        self.led2Threshold = p.led2Threshold
        self.led3Threshold = p.led3Threshold
        self.led4Threshold = p.led4Threshold
        self.frequency = p.frequency
        self.dutyCycle = p.dutyCycle
        self.duration = p.duration
        self.triggers = p.triggers
        self.elapsedSecondsAtEnd=p.elapsedSecondsAtEnd
        self.time=datetime.timedelta(seconds=self.duration)
        self.stepNumber = p.stepNumber

    def CopyProgramStepFromString(self,p):
        theSplit = p.split(',')
        try:
            if len(theSplit) == 8:
                self.led1Threshold = int(theSplit[0])
                self.led2Threshold = int(theSplit[1])
                self.led3Threshold = int(theSplit[2])
                self.led4Threshold = int(theSplit[3])
                self.frequency = int(theSplit[4])
                self.dutyCycle = int(theSplit[5])
                self.triggers = int(theSplit[6])
                self.duration = int(theSplit[7])
                self.elapsedSecondsAtEnd=self.duration
                self.time=datetime.timedelta(seconds=self.duration)
                self.stepNumber = 0
                return True
            else:
                return False
        except:
            return False

    def GetProgramStepString(self):
        s = '   Step = {:<3d}  Thresholds = {:<1d},{:<1d},{:<1d},{:<1d}  Freq = {:<3d}  Duty Cycle = {:<3d}  Triggers = {:<2d}  Duration = {:<5d}  Elapsed = {:<5.0f}'.format(self.stepNumber,self.led1Threshold,self.led2Threshold,self.led3Threshold,self.led4Threshold,self.frequency,self.dutyCycle,self.triggers,self.duration,self.elapsedSecondsAtEnd)
      
        return s

    def GetProgramStepArrayForUART(self):
        s= str(self.led1Threshold) + "," + str(self.led2Threshold) + "," + str(self.led3Threshold) + "," + str(self.led4Threshold) + ","+str(self.frequency) + "," +str(self.dutyCycle) + "," + str(self.triggers) + "," +str(self.duration) +",A"
        return bytearray(s.encode())
        
