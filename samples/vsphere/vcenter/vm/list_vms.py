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
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common.sample_util import pp
from com.vmware.vcenter_client import VM

"""
Demonstrates getting list of VMs present in vCenter
Sample Prerequisites:
vCenter/ESX
"""

stub_config = None
cleardata = False


def setup(context=None):
    global stub_config, cleardata
    server, username, password, cleardata, skip_verification = parse_cli_args()
    stub_config = vapiconnect.connect(server, username, password,
                                      skip_verification)
    atexit.register(vapiconnect.logout, stub_config)


def run():
    """
    List VMs present in server
    """
    vm_svc = VM(stub_config)
    list_of_vms = vm_svc.list()
    print("----------------------------")
    print("List Of VMs")
    print("----------------------------")
    for vm in list_of_vms:
        print('{}'.format(vm))
    print("----------------------------")


def main():
    setup()
    run()


if __name__ == '__main__':
    main()
