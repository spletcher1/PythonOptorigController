import Rig
import MyUART
import Program
import time
import datetime


theRig = Rig.OptoLifespanRig(1)
version ="2.0.x"

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
    print("done.\n",flush=True)
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
def CheckForErrors(optoRig,updateFirst):
    if updateFirst==True:
        optoRig.GetCurrentErrors()
    if optoRig.currentErrors != 0:
        print(optoRig.GetCurrentErrorString())    

def StopCommand():
    if theRig.SendStopProgram():
        print("Stop program signal sent and acknowledged.")
    else:
        print("Stop program signal sent but not acknowledged.")    
    CheckForErrors(theRig,False)   
def StageCommand():
    if theRig.SendStageProgram():
        print("Stage program signal sent and acknowledged.")
    else :
        print("Stage program signal sent but not acknowledged.")
    CheckForErrors(theRig,False)
def GetCommand():
    print(theRig.GetRemoteProgramString())    
    PrintCompareTest(theRig) 
    CheckForErrors(theRig,True)
def LocalCommand():
    print(theRig.GetLocalProgramString())    
    PrintCompareTest(theRig) 
def ClearCommand():
    if theRig.SendClearProgram():
        print("Clear program signal sent and acknowledged.")   
    else:
        print("Clear program signal sent but not acknowledged.")   
    CheckForErrors(theRig,False)
def SaveCommand():
    if theRig.SendSaveProgram():
        print("Save program signal sent and acknowledged.")   
    else:
        print("Save program signal sent but not acknowledged.")   
    CheckForErrors(theRig,False)
def LoadCommand():
    if theRig.SendLoadProgram():
        print("Load program signal sent and acknowledged.")   
    else:
        print("Load program signal sent but not acknowledged.")  
    CheckForErrors(theRig,False)     
def FirmwareCommand():
    print("Firmware version: "+ theRig.GetVersionInformationString())   
    print("Software version: "+ version)   
    CheckForErrors(theRig,True)    
def TimesCommand():
    s = "\n   Local time on rig: {}".format(theRig.GetRemoteRTCString())
    s+= "\nLocal time on master: {}\n".format(datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S"))
    print(s)   
    CheckForErrors(theRig,True)  
def ErrorsCommand():
    print(theRig.GetCurrentErrorString())   
def SetTimeCommand1Arg():
    s=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    if theRig.SendRTCSet(s):                    
        print("New datetime sent and acknowledged.")
        s = "\n   Local time on rig: {}".format(theRig.GetRemoteRTCString())
        s+= "\nLocal time on master: {}\n".format(datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S"))
        print(s)   
        CheckForErrors(theRig,True)  
    else:
        print("Problem sending new date and time. Check your formatting.")
def ClearErrorsCommand():
    if theRig.SendClearErrors():
        print("Clear errors signal sent and acknowledged.")   
    else:
        print("Clear errors signal sent but not acknowledged.")  
    print(theRig.GetCurrentErrorString())      
def UploadCommand():
    if theRig.UploadLocalProgram():
        print("Upload successful and acknowledged.")
        time.sleep(.5)
        print(theRig.GetRemoteProgramString())        
        PrintCompareTest(theRig)
        CheckForErrors(theRig,True) 
    else :
        print("Upload not successful.")               
def ChangeIDCommand():
    ChooseOptoRig(theRig) 
def LoadLocalCommand(arg1):
    theRig.LoadLocalProgram(arg1)
    print(theRig.GetLocalProgramString())                
    PrintCompareTest(theRig)   
def SetTimeCommand2Arg(argument1,argument2):
    s = argument1 +" "+argument2                              
    if theRig.SendRTCSet(s):                    
        print("New datetime sent and acknowledged.")
        s = "\n   Local time on rig: {}".format(theRig.GetRemoteRTCString())
        s+= "\nLocal time on master: {}\n".format(datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S"))
        print(s)   
        CheckForErrors(theRig,True)  
    else:
        print("Problem sending new date and time. Check your formatting.")   
def HelpCommand():
    
    print("\n\n  *** Available Commands (case insensitive) ***\n\n")
    print("            'Get' or 'Remote': Query and print currently loaded remote program.")
    print("                      'Stage': Stage currently loaded remote program.")
    print("                       'Stop': Stop/unstage currently loaded remote program.")    
    print("                       'Load': Load remote program from remote storage.")
    print("                       'Save': Save currently loaded remote program to remote storage.")
    print("                      'Clear': Remove currently loaded remote program.\n")
    
    print("              'Load filename': Load local program named \'filename\' to local device.")
    print("                      'Local': Print the currently loaded local program.")
    print("                     'Upload': Upload the currently loaded local program to the remote device.\n")
    
    
    print("     'Firmware' or 'Versions': Print the current versions of remote and local firmware/software.")
    print("                      'Times': Print the current time values on remote and local devices.")
    print("                     'Errors': Update and print the flagged errors from the remote device.\n")
    
    print("                    'Settime': Set the remote time to the current time on local device.")
    print("'Settime MM/DD/YYYY HH:MM:SS': Set the remote time to the given time.\n")
    
    print("                   'ChangeID': Change the ID of the currently targeted opto control board.\n")
    
    print("             'Exit' or 'Quit': Quit the app.\n\n")

def main():        
    ChooseSerialPort(theRig)
    ChooseOptoRig(theRig)            
    command="none"
    while command.lower() != "exit" and command.lower() != "quit":
        commandLine=input('> ')
        command=""
        argument = ""
        theSplit = commandLine.split()
        if len(theSplit)==1:
            command = theSplit[0].strip()
            if command.lower() == "stop":
                StopCommand()            
            elif command.lower()== 'stage':
                StageCommand()
            elif command.lower()== 'get' or command.lower()== 'remote':
                GetCommand()
            elif command.lower()== 'local':
                LocalCommand()                                    
            elif command.lower()== 'clear':
                ClearCommand()
            elif command.lower()== 'save':
                SaveCommand()
            elif command.lower()== 'load':
                LoadCommand()
            elif command.lower()== 'firmware' or command.lower()=="versions":                
                FirmwareCommand()
            elif command.lower()== 'times':
                TimesCommand()
            elif command.lower()== 'errors':
                ErrorsCommand()
            elif command.lower()=='settime':
                SetTimeCommand1Arg()
            elif command.lower()== 'clearerrors':
                ClearErrorsCommand()
            elif command.lower() == 'upload':
                UploadCommand()
            elif command.lower() == 'exit' or command.lower()=='quit':
                break
            elif command.lower() == 'changeid':
                ChangeIDCommand()  
            elif command.lower() == 'help':
                HelpCommand()                  
            else:
                print("Command not recognized.")                          
        elif len(theSplit)==2:
            command = theSplit[0].strip()
            argument = theSplit[1].strip()
            if command.lower() == 'load':                
                LoadLocalCommand(argument)      
            else:
                print("Command not recognized.")                
        elif len(theSplit)==3:
            command = theSplit[0].strip()
            argument1 = theSplit[1].strip()
            argument2 = theSplit[2].strip()
            if command.lower() == 'settime':  
                SetTimeCommand2Arg(argument1,argument2)
            else:
                print("Command not recognized.")                
        else:
            print("Command not recognized.")      

if __name__=="__main__" :
    main()
         