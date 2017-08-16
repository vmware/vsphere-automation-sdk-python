"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'

config = {}
config["SERVER"] = ""
config["USERNAME"] = "administrator@vsphere.local"
config["PASSWORD"] = "VMware1!"

config["ESX_HOST1"] = ""
config["ESX_HOST2"] = ""
config["ESX_USER"] = "root"
config["ESX_PASS"] = ""

config["USE_NFS"] = True
config["NFS_HOST"] = ""
config["NFS_REMOTE_PATH"] = "/store1"
config["NFS_DATASTORE_NAME"] = "Shared_NFS_Volume"

config["ESX_HOST1_VMFS_DATASTORE"] = "Local_VMFS_Volume_on_Host1"
config["ESX_HOST2_VMFS_DATASTORE"] = "Local_VMFS_Volume_on_Host2"

config["DATACENTER1_NAME"] = "Sample_DC_1"
config["DATACENTER2_NAME"] = "Sample_DC_2"

config["VM_FOLDER1_NAME"] = "Sample_VM_Folder_1"
config["VM_FOLDER2_NAME"] = "Sample_VM_Folder_2"

config["CLUSTER1_NAME"] = "Cluster1"

config["VDSWITCH1_NAME"] = "DSwitch1"
config["VDPORTGROUP1_NAME"] = "Static_Portgroup_on_DSwitch_1"

config["STDPORTGROUP_NAME"] = "VM Network"

# The main datacenter and datastore that will be used for the VM tests
config["VM_DATACENTER_NAME"] = config["DATACENTER2_NAME"]
config["VM_DATASTORE_NAME"] = config["NFS_DATASTORE_NAME"]

# GestOS should be one of the enumeration values in com.vmware.vcenter.vm.GuestOS
config["VM_GUESTOS"] = "WINDOWS_9_64"

config["VM_NAME_DEFAULT"] = "Sample_Default_VM_for_Simple_Testbed"
config["VM_NAME_BASIC"] = "Sample_Basic_VM_for_Simple_Testbed"
config["VM_NAME_EXHAUSTIVE"] = "Sample_Exhaustive_VM_for_Simple_Testbed"

config["BACKENDS_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]

# Root datastore path where VM backend files not will be created for the
# samples
config["BACKENDS_DATASTORE_ROOT_PATH"] = "[{}] Sample_Backends".format(config["VM_DATASTORE_NAME"])

config["DISK_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]
config["DISK_DATASTORE_ROOT_PATH"] = config["BACKENDS_DATASTORE_ROOT_PATH"] + "/disk"

config["ISO_SRC_URL"] = "https://dl.bintray.com/vmware/photon/iso/1.0TP2/x86_64/photon-minimal-1.0TP2.iso"
config["ISO_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]
config["ISO_DATASTORE_ROOT_PATH"] = config["BACKENDS_DATASTORE_ROOT_PATH"] + "/iso"
config["ISO_DATASTORE_PATH"] = config["ISO_DATASTORE_ROOT_PATH"] + "/photonOS.iso"

config["SERIAL_PORT_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]
config["SERIAL_PORT_DATASTORE_ROOT_PATH"] = config["BACKENDS_DATASTORE_ROOT_PATH"] + "/serial"
config["SERIAL_PORT_DATASTORE_PATH"] = config["SERIAL_PORT_DATASTORE_ROOT_PATH"] + "/serial.log"
config["SERIAL_PORT_NETWORK_SERVER_LOCATION"] = "tcp://localhost:16000"
config["SERIAL_PORT_NETWORK_CLIENT_LOCATION"] = "tcp://www.vmware.com:80"
config["SERIAL_PORT_NETWORK_PROXY"] = None

config["PARALLEL_PORT_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]
config["PARALLEL_PORT_DATASTORE_ROOT_PATH"] = config["BACKENDS_DATASTORE_ROOT_PATH"] + "/parallel"
config["PARALLEL_PORT_DATASTORE_PATH"] = config["PARALLEL_PORT_DATASTORE_ROOT_PATH"] + "/parallel.log"

config["FLOPPY_SRC_URL"] = "http://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/distributions/1.0/fdboot.img"
config["FLOPPY_DATACENTER_NAME"] = config["VM_DATACENTER_NAME"]
config["FLOPPY_DATASTORE_ROOT_PATH"] = config["BACKENDS_DATASTORE_ROOT_PATH"] + "/floppy"
config["FLOPPY_DATASTORE_PATH"] = config["FLOPPY_DATASTORE_ROOT_PATH"] + "/fdboot.img"


class Testbed(object):
    def __init__(self):
        self.config = {}
        self.entities = {}

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        """setting"""
        self._config = value

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        """setting"""
        self._entities = value

    def to_config_string(self):
        s = ["=" * 79,
             "Testbed Configuration:",
             "=" * 79]
        s += ["   {}: {}".format(k, self.config[k])
              for k in sorted(self.config.keys())]
        s += ["=" * 79]
        return "\n".join(s)

    def to_entities_string(self):
        s = ["=" * 79,
             "Testbed Entities:",
             "=" * 79]
        s += ["   {}: {}".format(k, self.entities[k])
              for k in sorted(self.entities.keys())]
        s += ["=" * 79]
        return "\n".join(s)

    def __str__(self):
        return "\n".join(self.to_config_string(),
                         self.to_entities_string())


_testbed = Testbed()
_testbed.config.update(config)


def get():
    return _testbed
