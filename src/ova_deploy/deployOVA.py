#!/usr/bin/env python

__author__ = "jeetsarkarHPE"

import os
import os.path
import ssl
import sys
import tarfile
import time
import yaml
from yaml.loader import SafeLoader

from threading import Timer
import six
import urllib
import requests


from pyVmomi import vim, vmodl
import atexit
from pyvim import connect

def readInputs():
    # Open the file and load the file
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data
    sys.exit()

def deployOVA(datacenter_choice, cluster_name, selectedDS, VMname, ovaURL):
    configInputs=readInputs()
    si = connect.SmartConnect(host=configInputs.get("hostname"),
                                            user=configInputs.get("username"),
                                            pwd=configInputs.get("password"),
                                            disableSslCertValidation=True)
    atexit.register(connect.Disconnect, si)

    # datacenter = si.content.rootFolder.childEntity[0]
    # datacenter_choice = int(input("Input Datacenter choice - 1 for Houston and 2 for Milpitas: "))
    if(datacenter_choice==1):
        datacenter = si.content.rootFolder.childEntity[0]
    else:
        datacenter = si.content.rootFolder.childEntity[1]

    resource_pool = get_largest_free_rp(si, datacenter)
    # cluster_name = input(f"Enter the cluster-name in {datacenter.name}: ")
    cluster = selectCluster(datacenter.hostFolder.childEntity,cluster_name)
    resource_pool = cluster.resourcePool
    # selectedDS = input(f"Enter the datastore in {cluster_name}: ")
    # VMname = input(f"Enter the VM Name in {cluster_name}: ")

    datastore = selectDataStore(datacenter.datastore,selectedDS)
    
    #selectedChoice = server_location(input("Enter the choice to be selected; 1 for Milpitas based server, 2 for Houston: "))

   # build_name = input("Enter the build name just before .ova ; ex: glcp-onprem-combined-1.0.0-10  or testing/glcp-onprem-combined-1.0.0-10 : ")

    ovf_handle = OvfHandler(ovaURL)

    ovf_manager = si.content.ovfManager
    # CreateImportSpecParams can specify many useful things such as
    # diskProvisioning (thin/thick/sparse/etc)
    # networkMapping (to map to networks)
    # propertyMapping (descriptor specific properties)
    cisp = vim.OvfManager.CreateImportSpecParams(entityName=VMname)
    cisr = ovf_manager.CreateImportSpec(
        ovf_handle.get_descriptor(), resource_pool, datastore, cisp)

    # These errors might be handleable by supporting the parameters in
    # CreateImportSpecParams
    if cisr.error:
        print("The following errors will prevent import of this OVA:")
        for error in cisr.error:
            print("%s" % error)
        return 1

    ovf_handle.set_spec(cisr)

    lease = resource_pool.ImportVApp(cisr.importSpec, datacenter.vmFolder)
    while lease.state == vim.HttpNfcLease.State.initializing:
        print(VMname + ": Waiting for lease to be ready...")
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        print(VMname + ": Lease error: %s" % lease.error)
        return 1
    if lease.state == vim.HttpNfcLease.State.done:
        return 0

    print(VMname + "Starting deploy...")
    return ovf_handle.upload_disks(lease, configInputs.get("hostname"))
    # ovf_handle.printter_func


def get_largest_free_rp(si, datacenter):
    """
    Get the resource pool with the largest unreserved memory for VMs.
    """
    view_manager = si.content.viewManager
    container_view = view_manager.CreateContainerView(datacenter, [vim.ResourcePool], True)
    largest_rp = None
    unreserved_for_vm = 0
    try:
        for resource_pool in container_view.view:
            if resource_pool.runtime.memory.unreservedForVm > unreserved_for_vm:
                largest_rp = resource_pool
                unreserved_for_vm = resource_pool.runtime.memory.unreservedForVm
    finally:
        container_view.Destroy()
    if largest_rp is None:
        raise Exception("Failed to find a resource pool in datacenter %s" % datacenter.name)
    return largest_rp


def selectDataStore(storeList, selectedDS):
    for i in storeList:
        if i.name == selectedDS:
            # print(type(i))
            # print(i.name)
            return i

def selectCluster(clusterList, selectedCluster):
    for i in clusterList:
        if i.name == selectedCluster:
            # print(i)
            # print(i.name)
            return i

def server_location(choice): 
        name = str
        if choice == 1:
           name = "16.182.31.122:9000" 
        else:
             name = "10.14.144.19"
        return name  

def get_tarfile_size(tarfile):
    """
    Determine the size of a file inside the tarball.
    If the object has a size attribute, use that. Otherwise seek to the end
    and report that.
    """
    if hasattr(tarfile, 'size'):
        return tarfile.size
    size = tarfile.seek(0, 2)
    tarfile.seek(0, 0)
    return size


class OvfHandler(object):
    """
    OvfHandler handles most of the OVA operations.
    It processes the tarfile, matches disk keys to files and
    uploads the disks, while keeping the progress up to date for the lease.
    """
    def __init__(self, ovafile):
        """
        Performs necessary initialization, opening the OVA file,
        processing the files and reading the embedded ovf file.
        """
        self.handle = self._create_file_handle(ovafile)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovffilename = list(filter(lambda x: x.endswith(".ovf"),
                                  self.tarfile.getnames()))[0]
        
        ovffile = self.tarfile.extractfile(ovffilename)
       
        self.descriptor = ovffile.read().decode()
        
    def _create_file_handle(self, entry):
        """
        A simple mechanism to pick whether the file is local or not.
        This is not very robust.
        """
        if os.path.exists(entry):
            return FileHandle(entry)
        return WebHandle(entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        """
        The import spec is needed for later matching disks keys with
        file names.
        """
        self.spec = spec
    
    def get_disk(self, file_item):
        """
        Does translation for disk key to file name, returning a file handle.
        """
        ovffilename = list(filter(lambda x: x == file_item.path,
                                  self.tarfile.getnames()))[0]
        return self.tarfile.extractfile(ovffilename)

    def get_device_url(self, file_item, lease):
        for device_url in lease.info.deviceUrl:
            if device_url.importKey == file_item.deviceId:
                return device_url
        raise Exception("Failed to find deviceUrl for file %s" % file_item.path)

    def upload_disks(self, lease, host):
        """
        Uploads all the disks, with a progress keep-alive.
        """
        self.lease = lease
        try:
            self.start_timer()
            for fileItem in self.spec.fileItem:
                self.upload_disk(fileItem, lease, host)
            lease.Complete()
            print("Finished deploy successfully.")
            return 0
        except vmodl.MethodFault as ex:
            print("Hit an error in upload: %s" % ex)
            lease.Abort(ex)
        except Exception as ex:
            print("Lease: %s" % lease.info)
            print("Hit an error in upload: %s" % ex)
            lease.Abort(vmodl.fault.SystemError(reason=str(ex)))
        return 1

    def upload_disk(self, file_item, lease, host):
        """
        Upload an individual disk. Passes the file handle of the
        disk directly to the urlopen request.
        """
        ovffile = self.get_disk(file_item)
        if ovffile is None:
            return
        device_url = self.get_device_url(file_item, lease)
        url = device_url.url.replace('*', host)
        headers = {'Content-length': get_tarfile_size(ovffile)}
        if hasattr(ssl, '_create_unverified_context'):
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None
        req = urllib.request.Request(url, ovffile, headers)
        urllib.request.urlopen(req, context=ssl_context)

    def start_timer(self):
        """
        A simple way to keep updating progress while the disks are transferred.
        """
        Timer(5, self.timer).start()

    def timer(self):
        """
        Update the progress and reschedule the timer if not complete.
        """
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done,
                                        vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progress: %d%%\r" % prog)
        except Exception:  # Any exception means we should stop updating progress.
            pass


class FileHandle(object):
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'rb')

        self.st_size = os.stat(filename).st_size
        self.offset = 0

    def __del__(self):
        self.fh.close()

    def tell(self):
        return self.fh.tell()

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset

        return self.fh.seek(offset, whence)

    def seekable(self):
        return True

    def read(self, amount):
        self.offset += amount
        result = self.fh.read(amount)
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)


class WebHandle(object):
    def __init__(self, url):
        self.url = url
        r = urllib.request.urlopen(url)
        if r.code != 200:
            raise FileNotFoundError(url)
        self.headers = self._headers_to_dict(r)
        if 'accept-ranges' not in self.headers:
            raise Exception("Site does not accept ranges")
        self.st_size = int(self.headers['content-length'])
        self.offset = 0

    def _headers_to_dict(self, r):
        result = {}
        if hasattr(r, 'getheaders'):
            for n, v in r.getheaders():
                result[n.lower()] = v.strip()
        else:
            for line in r.info().headers:
                if line.find(':') != -1:
                    n, v = line.split(': ', 1)
                    result[n.lower()] = v.strip()
        return result

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset
        return self.offset

    def seekable(self):
        return True

    def read(self, amount):
        start = self.offset
        end = self.offset + amount - 1
        req = urllib.request.Request(self.url,
                      headers={'Range': 'bytes=%d-%d' % (start, end)})
        r = urllib.request.urlopen(req)
        self.offset += amount
        result = r.read(amount)
        r.close()
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)
