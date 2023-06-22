#!/bin/python3
# Copyright (c)
# title           : app.py
# description     : Main File
# author          : Sachinthra
# date            : 20/06/2023
# =========================================================

import time
import yaml
from components.paramikoClient import ParamikoClient

# Reading Inputs from input.yaml
with open("src/input.yaml", "r") as stream:
    try:
        data = yaml.safe_load(stream)
        HOSTNAME = data["HOSTNAME"]
        FQDN = data["FQDN"]
        USERNAME = data["USERNAME"]
        PASSWORD = data["PASSWORD"]
        TARBALL_PATH = data["TARBALL_PATH"]
        NTP_SERVER = data["NTP_SERVER"]
        CLI_PASSWORD = data["CLI_PASSWORD"]
        print(HOSTNAME,FQDN,USERNAME,PASSWORD,TARBALL_PATH,NTP_SERVER,CLI_PASSWORD)
    except yaml.YAMLError as exc:
        print(exc)


# Object creation
print("Connecting to "+HOSTNAME)
obj = ParamikoClient(
    hostname=HOSTNAME,
    username=USERNAME,
    password=PASSWORD
)

print("Connect done to "+HOSTNAME)

# this function is for creating the Temp Root shell which is Option 8 in the main menu.
def tempRootShell():
    obj.waitAndExecute(string="8. Temporary Root Shell", inputString=8)
    obj.waitAndExecute(
        string="This will reset the previous Onprem root shell's pwd. proceed? (y/n):", inputString="y")
    obj.waitAndExecute(
        string="Press [Enter] key to continue...", inputString="")

    print("Done Temp Root Shell")


def toMainMenu():
    obj.waitAndExecute(string="Enter option ", inputString="m")

# This function is for SCP APP TAR ball to the VM before installation process.


def executeScpFile():
    obj.waitAndExecute(string="2. File Operations", inputString=2)
    obj.waitAndExecute(string="1. Upload via (SCP)", inputString=1)
    obj.waitAndExecute(
        string="Enter remote hostname and path (username@hostname:<filepath>)", inputString=TARBALL_PATH)

    # after entering the TAR file path. check if it asks for the key geeration -> write "yes" then password. if key already there then write the password.
    if obj.waitForString("Are you sure you want to continue connecting (yes/no)?", False):
        obj.executeInput("yes")
        obj.waitAndExecute(string="password", inputString="ssmssm99")
    else:
        obj.executeInput("ssmssm99")

    # Wait untill the process completes
    obj.waitAndExecute(
        string="Press [Enter] key to continue...", inputString="", waitLoop=100, interval=10)


def installTAR():
    obj.waitAndExecute(string="6. Install Onprem Software", inputString=6)
    obj.waitAndExecute(
        string="Use number to select a file or 'stop' to cancel:", inputString=1)

    obj.waitAndExecute(
        string="Press [Enter] key to continue...", inputString="", waitLoop=300, interval=60)
    time.sleep(60)
    print("Done")


def restartMenu():
    obj.closeConnection()
    obj.openConnection(HOSTNAME, USERNAME, PASSWORD)

# Runs Setup cluster step by step
def clusterSetup():
    obj.waitAndExecute(string="7. Setup Cluster", inputString=7)
    obj.waitAndExecute(string="Enter primary NTP server",
                       inputString=NTP_SERVER)
    obj.waitAndExecute(
        string="Enter secondary NTP server (Optional):", inputString="")
    obj.waitAndExecute(
        string="Is NTP Authentication required (y/n) :", inputString="n")
    obj.waitAndExecute(string="Enter cluster FQDN :", inputString=FQDN)
    obj.waitAndExecute(string="Please enter CLI password:",
                       inputString=CLI_PASSWORD)
    obj.waitAndExecute(string="Please re-enter CLI password",
                       inputString=CLI_PASSWORD)
    obj.waitAndExecute(
        string="Please enter UI admin password:", inputString=CLI_PASSWORD)
    obj.waitAndExecute(
        string="Please re-enter UI admin password", inputString=CLI_PASSWORD)
    obj.waitAndExecute(string="Enter Pod IP Range", inputString="")
    obj.waitAndExecute(string="Enter Service IP Range", inputString="")
    obj.waitForString("Press [Enter] key to continue...",
                      waitLoop=300, interval=60*5)

def displayMenu():
    print("1. Temp Root Shell -> TAR SCP -> Install TAR" +
          "2. Custer Setup")
    x = input("Enter the option")
    if x == 1:
        tempRootShell()
        toMainMenu()
        executeScpFile()
        toMainMenu()
        installTAR()
    elif x ==2:
        clusterSetup()
    else:
        print("Exiting")


displayMenu()
# tempRootShell()
# toMainMenu()
# executeScpFile()
# toMainMenu()
# installTAR()
# # not workings
# toMainMenu()

# obj.waitAndExecute(string="Enter option ", inputString="0")

# restartMenu()
# clusterSetup()


# obj.waitForString("Enter option ")
