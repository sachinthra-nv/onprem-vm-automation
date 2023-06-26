#!/bin/python3
# Copyright (c)
# title           : app.py
# description     : Main File
# author          : Sachinthra
# date            : 20/06/2023
# =========================================================

import time
from components.paramikoClient import ParamikoClient
from components.appLogging import stepLogger

class FlowFunctions:
    def __init__(self, obj, fqdn, tarBallPath, ntp_Server, cli_password):
        if not isinstance(obj, ParamikoClient):
            stepLogger.error("obj must be an instance of ParamikoClient")
            raise ValueError("obj must be an instance of ParamikoClient")
        self.obj = obj
        self.fqdn = fqdn
        self.tarBallPath = tarBallPath
        self.ntp_Server = ntp_Server
        self.cli_password = cli_password

    # this function is for creating the Temp Root shell which is Option 8 in the main menu.
    def tempRootShell(self):
        stage = "Temp Root Shell"
        stepLogger.info("Starting "+stage)
        self.obj.waitAndExecute(
            string="8. Temporary Root Shell", inputString=8)
        self.obj.waitAndExecute(
            string="This will reset the previous Onprem root shell's pwd. proceed? (y/n):", inputString="y")
        self.obj.waitAndExecute(
            string="Press [Enter] key to continue...", inputString="")

        stepLogger.info("Done "+stage)
        print("Done "+stage)

    def toMainMenu(self):
        stage = "Going to Main Menu"
        stepLogger.info(stage)
        self.obj.waitAndExecute(string="Enter option ", inputString="m")
        stepLogger.info("Done "+stage)

    # This function is for SCP APP TAR ball to the VM before installation process.

    def executeScpFile(self):
        stage = "SCP TAR"
        stepLogger.info("Starting "+stage)
        self.obj.waitAndExecute(string="2. File Operations", inputString=2)
        self.obj.waitAndExecute(string="1. Upload via (SCP)", inputString=1)
        self.obj.waitAndExecute(
            string="Enter remote hostname and path (username@hostname:<filepath>)", inputString=self.tarBallPath)

        # after entering the TAR file path. check if it asks for the key geeration -> write "yes" then password. if key already there then write the password.
        if self.obj.waitForString("Are you sure you want to continue connecting (yes/no)?", False):
            self.obj.executeInput("yes")
            self.obj.waitAndExecute(string="password", inputString="ssmssm99")
        else:
            self.obj.executeInput("ssmssm99")

        # Wait untill the process completes
        self.obj.waitAndExecute(
            string="Press [Enter] key to continue...", inputString="", waitLoop=100, interval=10)
        
        stepLogger.info("Done "+stage)

    def installTAR(self):
        stage = "Install TAR"
        stepLogger.info("Starting "+stage)
        self.obj.waitAndExecute(
            string="6. Install Onprem Software", inputString=6)
        self.obj.waitAndExecute(
            string="Use number to select a file or 'stop' to cancel:", inputString=1)

        self.obj.waitAndExecute(
            string="Press [Enter] key to continue...", inputString="", waitLoop=2000, interval=10)
        
        time.sleep(10)

        stepLogger.info("Done "+stage)

    def restartMenu(self):
        self.obj.closeConnection()
        self.obj.openConnection(
            self.obj.hostname, self.obj.username, self.obj.password)

    # Runs Setup cluster step by step
    def clusterSetup(self):
        stage = "Cluster Setup"
        stepLogger.info("Starting "+stage)
        self.obj.waitAndExecute(string="7. Setup Cluster", inputString=7)
        self.obj.waitAndExecute(string="Enter primary NTP server",
                                inputString=self.ntp_Server)
        self.obj.waitAndExecute(
            string="Enter secondary NTP server (Optional):", inputString="")
        self.obj.waitAndExecute(
            string="Is NTP Authentication required (y/n) :", inputString="n")
        self.obj.waitAndExecute(
            string="Enter cluster FQDN :", inputString=self.fqdn)
        self.obj.waitAndExecute(string="Please enter CLI password:",
                                inputString=self.cli_password)
        self.obj.waitAndExecute(string="Please re-enter CLI password",
                                inputString=self.cli_password)
        self.obj.waitAndExecute(
            string="Please enter UI admin password:", inputString=self.cli_password)
        self.obj.waitAndExecute(
            string="Please re-enter UI admin password", inputString=self.cli_password)
        self.obj.waitAndExecute(string="Enter Pod IP Range", inputString="")
        self.obj.waitAndExecute(
            string="Enter Service IP Range", inputString="")
        self.obj.waitForString("Press [Enter] key to continue...",
                               waitLoop=300, interval=60*5)
        time.sleep(10)
        stepLogger.info("Done " + stage)
