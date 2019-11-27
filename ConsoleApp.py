import Rig
import MyUART
import Program



def ChooseSerialPort(optoRig):
    while True:
        ports=optoRig.thePort.GetAvailablePorts()
        print('Please choose available serial port:')
        index=1
        for p in ports:
            print('  {:d}. {}'.format(index,p))
        choice=int(input('> '))-1
        if choice>=0 and choice < len(ports):
            optoRig.thePort.Open(ports[choice])
            break
        else:
            print("Invalid choice! Try again.\n")

def ChooseOptoRig(optoRig):   
    print("Searching for opto control boards...", end="",flush=True)
    tmp = optoRig.GetListOfOnlineRigs()
    print("done.",flush=True)
    while True:
        print('Please choose available serial optorig:')
        for num in list(tmp):
            print('   {:d}. ID = {:d}; Firmware version = {}'.format(num,num,tmp[num]))
        choice=int(input('> '))
        if tmp.get(choice,-1) != -1:
            optoRig.ID = choice
            break
        else:
            print("Invalid choice! Try again.\n")    



if __name__=="__main__" :
    theRig = Rig.OptoLifespanRig(14)
    theRig.localProgram.LoadLocalProgram(".\program.txt")
    #ChooseSerialPort(theRig)
    theRig.thePort.Open('/dev/ttyUSB0')
    #ChooseOptoRig(theRig)
    #print(theRig.GetVersionInformationString())
    print(theRig.GetRemoteProgramString())
    #theRig.SendProgramStep(theRig.remoteProgram.fullProgramSteps[0])
    #print(theRig.GetRemoteProgramString())
    