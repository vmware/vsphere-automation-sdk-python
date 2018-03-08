"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
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
__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import VM


def get_vm(client, vm_name):
    """
    Return the identifier of a vm
    Note: The method assumes that there is only one vm with the mentioned name.
    """
    names = set([vm_name])
    vms = client.vcenter.VM.list(VM.FilterSpec(names=names))

    if len(vms) == 0:
        print("VM with name ({}) not found".format(vm_name))
        return None

    vm = vms[0].vm
    print("Found VM '{}' ({})".format(vm_name, vm))
    return vm


def get_vms(client, vm_names):
    """Return identifiers of a list of vms"""
    vms = client.vcenter.VM.list(VM.FilterSpec(names=vm_names))

    if len(vms) == 0:
        print('No vm found')
        return None

    print("Found VMs '{}' ({})".format(vm_names, vms))
    return vms
