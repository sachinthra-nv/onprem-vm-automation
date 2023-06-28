import yaml
import sys
from yaml.loader import SafeLoader
from threading import Thread
from deployOVA import deployOVA
from destroy import destroyVM

THREADING=True

def readInputs():
    # Open the file and load the file
    with open('input.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data

def createVMs(vmList, ovaURL):
    thread = {}
    for vm in vmList:
        vm = vm.get("vm")
        # print("datacenter : "+str(vm.get("datacenter")))
        # print("clustername : "+vm.get("clustername"))
        # print("datastore : "+vm.get("datastore"))
        # print("name : "+vm.get("name"))
        if THREADING:
            thread[vm.get("name")] = Thread(target=deployOVA, args=(vm.get("datacenter"), vm.get("clustername"), vm.get("datastore"), vm.get("name"), ovaURL))
            thread[vm.get("name")].start()
        else:
            deployOVA(datacenter_choice=vm.get("datacenter"), cluster_name=vm.get("clustername"), selectedDS=vm.get("datastore"), VMname=vm.get("name"), ovaURL=ovaURL)
    if THREADING:
        for vm in vmList:
            name = vm.get("vm").get("name")
            thread[name].join()


def deleteVMs(vmList):
    thread = {}
    for vm in vmList:
        vm = vm.get("vm")
        # print(vm.get("name"))
        # print(vm.get("datacenter"))
        if THREADING:
            thread[vm.get("name")] = Thread(target=destroyVM, args=(vm.get("datacenter"), vm.get("name")))
            thread[vm.get("name")].start()
        else:
            destroyVM(datacenter_choice=vm.get("datacenter"), vmname=vm.get("name"))
    if THREADING:
        for vm in vmList:
            name = vm.get("vm").get("name")
            thread[name].join()



def main():
    # check for THREADING=True/False
    inputData = readInputs()
    deleteVMs(inputData.get("vms").get("destroy"))
    print("Done Deleting")
    
    createVMs(inputData.get("vms").get("create"), inputData.get("ovaURL"))
    print("Done Creating")

if __name__ == "__main__":
    sys.exit(main())