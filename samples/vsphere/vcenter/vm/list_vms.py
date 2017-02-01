#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""
import atexit

from com.vmware.vcenter.vm_client import Power
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates getting list of VMs present in vCenter

Sample Prerequisites:
vCenter/ESX
"""

#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

from com.vmware.vcenter.vm.hardware.boot_client import Device as BootDevice
from com.vmware.vcenter.vm.hardware_client import (
    Disk, Ethernet)
from com.vmware.vcenter.vm.hardware_client import ScsiAddressSpec
from com.vmware.vcenter.vm_client import (Power)
from com.vmware.vcenter_client import VM
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to List the VMs present in a vCenter server:

Sample Prerequisites:
    - VC
    - ESX
    - datacenter
"""

stub_config = None


def setup(context=None):
    global stub_config, cleardata
    server, username, password, cleardata, skip_verification = \
        parse_cli_args()
    stub_config = vapiconnect.connect(server,
                                      username,
                                      password,
                                      skip_verification)


def run():
    list_vms(stub_config)


def list_vms(stub_config):
    """
    List VMs present in server
    
    """
    vm_svc = VM(stub_config)
    list_of_vms = vm_svc.list()
    for vm in list_of_vms:
        print ('{}'.format(vm))


def cleanup():
    pass


def main():
    try:
        setup()
        cleanup()
        run()
        if cleardata:
            cleanup()
    finally:
        if stub_config:
            vapiconnect.logout(stub_config)


if __name__ == '__main__':
    main()