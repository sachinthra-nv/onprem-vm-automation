#!/bin/python3
# Copyright (c)
# title           : app.py
# description     : Main File
# author          : Sachinthra
# date            : 20/06/2023
# =========================================================

import yaml
from components.paramikoClient import ParamikoClient
from components.flowFunctions import FlowFunctions
from components.appLogging import stepLogger


def doFlow(paramikoClientObj, flowFunctionsobj):
    stepLogger.info("Starting Flow")
    flowFunctionsobj.tempRootShell()
    flowFunctionsobj.toMainMenu()
    flowFunctionsobj.executeScpFile()
    flowFunctionsobj.toMainMenu()
    flowFunctionsobj.installTAR()
    # paramikoClientObj.reOpenConnection()
    # flowFunctionsobj.clusterSetup()
    stepLogger.info("Exiting Flow")


def main():
    # Reading Inputs from input.yaml
    try:
        stepLogger.info("Reading input.yaml")
        with open("src/input.yaml", "r") as stream:
            data = yaml.safe_load(stream)
            HOSTNAME = data["HOSTNAME"]
            FQDN = data["FQDN"]
            USERNAME = data["USERNAME"]
            PASSWORD = data["PASSWORD"]
            TARBALL_PATH = data["TARBALL_PATH"]
            NTP_SERVER = data["NTP_SERVER"]
            CLI_PASSWORD = data["CLI_PASSWORD"]
            print(HOSTNAME, FQDN, USERNAME, PASSWORD,
                  TARBALL_PATH, NTP_SERVER, CLI_PASSWORD)
    except yaml.YAMLError as exc:
        print(exc)
        stepLogger.error(str(exc))
        quit()

    # Object creation
    try:
        print("Connecting to "+HOSTNAME)
        paramikoClientObj = ParamikoClient(
            hostname=HOSTNAME,
            username=USERNAME,
            password=PASSWORD
        )
        print("Connected to "+HOSTNAME)
    except Exception as e:
            print(e)
            stepLogger.error(str(e))
            quit()

    try:
        flowFunctionsobj = FlowFunctions(
            obj=paramikoClientObj,
            fqdn=FQDN,
            tarBallPath=TARBALL_PATH,
            ntp_Server=NTP_SERVER,
            cli_password=CLI_PASSWORD
        )
    except Exception as e:
            print(e)
            stepLogger.error(str(e))
            quit()

    doFlow(paramikoClientObj, flowFunctionsobj)


if __name__ == "__main__":
    main()
