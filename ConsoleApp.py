import Rig
import MyUART
import Program
import time


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

def PrintCompareTest(optoRig):
    if optoRig.AreLocalAndRemoteProgramsIdentical():
        print("Local and remote programs are identical.")
    else:
        print("Local and remote programs are different.")



if __name__=="__main__" :
    theRig = Rig.OptoLifespanRig(1)
    #ChooseSerialPort(theRig)
    #ChooseOptoRig(theRig)    
    theRig.thePort.Open('/dev/ttyUSB0')
    
    #theRig.LoadLocalProgram("TestProgram.txt")
    #print(theRig.GetLocalProgramString())
    #theRig.UploadLocalProgram()
    #print(theRig.GetRemoteProgramString())

    command="none"
    while command.lower() != "exit" and command.lower() != "quit":
        commandLine=input('> ')
        command=""
        argument = ""
        theSplit = commandLine.split()
        if len(theSplit)==1:
            command = theSplit[0].strip()
            if command.lower() == "stop":
                theRig.SendStopProgram()
                print("Stop program signal sent.")
            elif command.lower()== 'stage':
                theRig.SendStageProgram()
                print("Stage program signal sent.")
            elif command.lower()== 'get' or command.lower()== 'remote':
                print(theRig.GetRemoteProgramString())    
                PrintCompareTest(theRig) 
            elif command.lower()== 'local':
                print(theRig.GetLocalProgramString())    
                PrintCompareTest(theRig)                           
            elif command.lower()== 'clear':
                theRig.SendClearProgram()
                print("Clear program signal sent.")   
            elif command.lower()== 'save':
                theRig.SendSaveProgram()
                print("Save program signal sent.")   
            elif command.lower()== 'load':
                theRig.SendLoadProgram()
                print("Load program signal sent.")   
            elif command.lower()== 'firmware':                
                print("Firmware version: "+ theRig.GetVersionInformationString())   
            elif command.lower()== 'rtc':
                print(theRig.GetRemoteRTCString())                
            elif command.lower() == 'upload':
                theRig.UploadLocalProgram()
                time.sleep(1)
                print(theRig.GetRemoteProgramString())        
                PrintCompareTest(theRig)
            elif command.lower() == 'exit':
                break
            else:
                print("Command not recognized.")                          
        elif len(theSplit)==2:
            command = theSplit[0].strip()
            argument = theSplit[1].strip()
            if command.lower() == 'load':                
                theRig.LoadLocalProgram(argument)
                print(theRig.GetLocalProgramString())                
                PrintCompareTest(theRig)
            else:
                print("Command not recognized.")                
        else:
            print("Command not recognized.")            
        


    #theRig.localProgram.LoadLocalProgram("TestProgram3.txt")
    #theRig.UploadLocalProgram()
    #time.sleep(1)
    #print(theRig.GetRemoteProgramString())
    #print(theRig.localProgram.IsProgramIdentical(theRig.remoteProgram))

    #theRig.thePort.Open('/dev/ttyUSB0')
    #print(theRig.GetVersionInformationString())
    #print(theRig.GetRemoteProgramString())
    #theRig.SendProgramStep(theRig.remoteProgram.fullProgramSteps[0])
    #print(theRig.GetRemoteProgramString())
    