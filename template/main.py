#author          : Sachinthra
#date            : 20/06/2023
#=========================================================

import paramiko
import time
import select

# Limit For the read -> connection.recv(BYTELIMIT)
BYTELIMIT=10000

class ParamikoClient:
    #  Will Configure a SSH and Establish a connection.
    def __init__(self,hostname,username,password,port=22):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy() )
        self.ssh.connect(hostname, port, username, password)
        self.conn = self.invoke_shell()
        
    # For declaring invoke_shell Instance
    def invoke_shell(self):
        # stdin = ssh.exec_command("")
        # Note: I am using invoke_shell not exec_command
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

# Object creation
obj = ParamikoClient(hostname="10.14.144.67",username="cliadmin",password="onpremccs@123")
print("Connect done")

# this function is for creating the Temp Root shell which is Option 8 in the main menu.
def tempRootShell():
    obj.waitForString("8. Temporary Root Shell")
    obj.executeOption(8)
    obj.waitForString("This will reset the previous Onprem root shell's pwd. proceed? (y/n):")
    obj.executeOption("y")
    obj.waitForString("Press [Enter] key to continue...")
    print("Done Temp Root Shell")
    # print(obj.displayEmpty())

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
    

tempRootShell()
# executeScpFile()


