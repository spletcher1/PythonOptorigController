import Rig
import MyUART
import Program
import time

theRig = Rig.OptoLifespanRig(15)
theRig.thePort.Open("/dev/ttyUSB0")
index=1
while True:
    print("Round: " + str(index))
    if theRig.GetVersionInformationString() == "No response":
        theRig.GetCurrentErrors()
        print(theRig.GetCurrentErrorString())
    time.sleep(2)
    index=index+1


settime 10/24/2019 11:54:23