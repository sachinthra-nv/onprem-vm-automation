#Copyright (c) 
#title           : paramikoClient.py
#description     : ParamikoClient Class
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
        self.ssh = {}
        self.conn = {}
        self.openConnection(hostname, username, password, port)
    
    # To establish a connection and declare ssh and connection
    def openConnection(self,hostname,username,password,port=22):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy() )
        ssh.connect(hostname, port, username, password)
        self.ssh = ssh
        self.conn = self.invoke_shell()
    
    # To close a ssh.
    def closeConnection(self):
        self.ssh.close()
        
    # For declaring invoke_shell Instance
    def invoke_shell(self):
        # stdin = ssh.exec_command("")
        return self.ssh.invoke_shell()

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
    def executeInput(self, string):
        # This Writes the value and enters it.
        self.conn.send(str(string)+"\n")
        time.sleep(2)

    # This Waits until the read input matchs the [string] we feed it. It has timeout/retries also. 
    # string = String to search for.
    # interval = For each loop is the [string] is not matched then wait for some time.
    # waitLoop = Number of times/loop it should fetch the output from the connection
    # isExit = After [waitLoop] is done if it is True the it quits the program. if false then returns False. which will be handy sometimes. 
    def waitForString(self, string, isExit=True, waitLoop=5, interval=2):
        curLoop=0
        # Runs a loop for [waitLoop]
        while curLoop<waitLoop:
            # gets the output from the [connection]
            op = self.receive_with_timeout(self.conn)
            print(str(op))
            # Check if Given string is present in the output and return  true
            if op != "" and string in op:
                return True
            else:
                # if not above wait for the [interval]
                time.sleep(interval)
            # upgrade the [curLoop] for loop back
            curLoop=curLoop+1
        # if No string was found and [isExit] is true then exit the program
        if isExit:
            print("Exit 1")
            quit()
        return False

    # string = String to search for.
    # inputString = string to write when [string] is found in the output
    # interval = For each loop is the [string] is not matched then wait for some time.
    # waitLoop = Number of times/loop it should fetch the output from the connection
    # isExit = After [waitLoop] is done if it is True the it quits the program. if false then returns False. which will be handy sometimes. 
    def waitAndExecute(self, string, inputString, isExit=True, waitLoop=5, interval=2):
        if self.waitForString(string=string, isExit=isExit, waitLoop=waitLoop, interval=interval):
            self.executeInput(inputString)



