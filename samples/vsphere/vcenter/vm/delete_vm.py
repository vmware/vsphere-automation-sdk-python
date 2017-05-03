#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: MIT
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
from samples.vsphere.common.sample_util import parse_cli_args_vm
from com.vmware.vcenter_client import VM
from com.vmware.vcenter.vm_client import Power
from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates Deleting User specified Virtual Machine (VM)
Sample Prerequisites:
vCenter/ESX
"""

stub_config = None
vm_name = None
vm = None


def setup(context=None):
    global stub_config, vm_name
    server, username, password, cleardata, skip_verification, vm_name = \
        parse_cli_args_vm(vm_name)
    stub_config = vapiconnect.connect(server, username, password,
                                      skip_verification)
    atexit.register(vapiconnect.logout, stub_config)


def run():
    """
    Delete User specified VM from Server
    """
    global vm
    vm_svc = VM(stub_config)
    power_svc = Power(stub_config)
    vm = get_vm(stub_config, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}).'
                        'Please create the vm first.'.format(vm_name))
    print("Deleting VM -- '{}-({})')".format(vm_name, vm))
    state = power_svc.get(vm)
    if state == Power.Info(state=Power.State.POWERED_ON):
        power_svc.stop(vm)
    elif state == Power.Info(state=Power.State.SUSPENDED):
        power_svc.start(vm)
        power_svc.stop(vm)
    vm_svc.delete(vm)
    print("Deleted VM -- '{}-({})".format(vm_name, vm))


def main():
    setup()
    run()


if __name__ == '__main__':
    main()
