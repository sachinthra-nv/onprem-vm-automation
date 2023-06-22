# onprem-vm-automation

## Exp
> Before running this code `Network Setup` step should be completed.
#### Steps to Run the program
`app.py` is the entry point fo the program.

To Run
```bash 
python3 src/app.py
```
After running it will show a menu.
```bash

```
> **_NOTE:_** Currently this code cant continue from Install TAR to Cluster Setup. So, We need to re run the program and choose the next option in order to continue. 

When you choose option 1, It Runs the steps like 
1. Temp Root Shell
1. Back To Main Menu
1. Scp TAR File
1. Back To Main Menu
1. Install TAR 

and for Option 2
1. cluster Setup

This code works like, Read -> check if it have given string: if it has then do this: if not read the next set of output printed and loop back.
```py
# In ParamikoClient class
# string = String to search for.
# inputString = string to write when [string] is found in the output
# interval = For each loop is the [string] is not matched then wait for some time.
# waitLoop = Number of times/loop it should fetch the output from the connection
# isExit = After [waitLoop] is done if it is True the it quits the program. if false then returns False. which will be handy sometimes. 
def waitAndExecute(self, string, inputString, isExit=True, waitLoop=5, interval=2)
```

---
### Limitations 
1. This code does not have any Fail Safe case written. Eg. If the Installation fails (Was not able to )
1. There is no contineous process from Install TAR to Cluster Setup.
---
### Template Code Explain

File Name `template/main.py` -> this file contains all the code.

---
##### Library Used
```py
import paramiko # Used for SSHClient
import time     
import select   # Used to include TIMEOUT for reading the input
```

##### Limit For the read -> connection.recv(BYTELIMIT)
```py
BYTELIMIT=10000
```
---
##### ParamikoClient -> For SSH connection and other functions which can be used for READ/WRITE process
```py
class ParamikoClient:
    # Initialize class -> Will Configure a SSH and Establish a connection.
    # Arguments 
    #   - hostname = IP address of the VM we need to automate
    #   - username = User Name address of the VM we need to automate
    #   - password = Password address of the VM we need to automate
    #   - port     = Default post will be 22
    def __init__(self, hostname, username, password, port=22):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy() )
        self.ssh.connect(hostname, port, username, password)
        self.conn = self.invoke_shell()
        
    # For declaring invoke_shell Instance
    def invoke_shell(self):
        # Usually below commented line is used if you’re going to execute a single command
        # stdin = ssh.exec_command("")

        # Note: I am using invoke_shell not exec_command 
        # Request a pseudo-terminal from the server.
        return self.ssh.invoke_shell()

    # Read the Output from the connection. 
    # - This is like a pointer. If it reads something once you can't the string again. 
    #       eg. Assume at the time when we run this function, 
    #       shell has is "AB" it will read "AB" and next time 
    #       when youn read again assume, it has 2 new char "CD" So "ABCD" now it will read only "CD".
    # - this function also includes Timeout=2. Usually it waits until there is some input to read if there is no value to read it waits untill it has some.
    def receive_with_timeout(self, connection, timeout=2):
        ready, _, _ = select.select([connection], [], [], timeout)
        if ready:
            # print(output.replace("\\r", "").replace("\\n", "\n"))
            return str(connection.recv(BYTELIMIT)).replace("\\r", "").replace("\\n", "\n").replace("\\x1b[H\\x1b[J","")
        else:
            return ""
    
    # For Debuging Purposes 
    def displayEmpty(self):
        return self.receive_with_timeout(self.conn)

    # This writes the [string] and press `enter`then Sleeps for 2 Sec to give some time to display the output. 
    def executeOption(self, string):
        self.conn.send(str(string)+"\n")
        time.sleep(2)

    # This Waits until the read input matchs the [string] we feed it. It has timeout/retries also. 
    def waitForString(self, string, exit=True,waitTime=5,interval=2):
        t=0
        while t<waitTime:
            op = self.receive_with_timeout(self.conn)
            print(str(op))
            if op != "" and string in op:
                return True
            else:
                time.sleep(interval)
            t=t+1
        if exit:
            quit()
        return False
```

---
##### Implementing Logic

```py
# Object creation
obj = ParamikoClient(hostname="10.14.144.67",username="cliadmin",password="onpremccs@123")
print("Connect done")
```

###### 1. Temp Root Shell
```py
# this function is for creating the Temp Root shell which is Option 8 in the main menu.
def tempRootShell():
    obj.waitForString("8. Temporary Root Shell")
    obj.executeOption(8)
    obj.waitForString("This will reset the previous Onprem root shell's pwd. proceed? (y/n):")
    obj.executeOption("y")
    obj.waitForString("Press [Enter] key to continue...")
    print("Done Temp Root Shell")
    # print(obj.displayEmpty())
```
###### 2. SCP TAR BALL
```py
# This function is for SCP APP TAR ball to the VM before installation process.
def executeScpFile():
    obj.waitForString("2. File Operations")
    obj.executeOption(2)
    obj.waitForString("1. Upload via (SCP)")
    obj.executeOption(1)
    obj.waitForString("Enter remote hostname and path (username@hostname:<filepath>)")
    obj.executeOption("esroot@16.182.31.122:/home/esroot/sachinthra/onborad/send.tar.gz")
    # after entering the TAR file path. check if it asks for the key geeration -> write "yes" then password. if key already there then write the password.
    if obj.waitForString("Are you sure you want to continue connecting (yes/no)?",False):
        obj.executeOption("yes")
        obj.waitForString("password")
        obj.executeOption("ssmssm99")
    else:
        obj.executeOption("ssmssm99")
    # Wait untill the process completes 
    obj.waitForString("Press [Enter] key to continue...",waitTime=100,interval=60*5)
```
---


