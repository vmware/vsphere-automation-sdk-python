#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
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
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm_client import Power
from com.vmware.vcenter_client import VM
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.helper import vm_placement_helper
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to create a VM with system provided defaults

Sample Prerequisites:
    - datacenter
    - vm folder
    - datastore
    - cluster
    - standard switch network
"""

stub_config = None
cleardata = False
vm_name = None


def setup(context=None):
    global stub_config, cleardata, vm_name
    if context:
        # Run sample suite via setup script
        vm_name = testbed.config['VM_NAME_DEFAULT']
        stub_config = context.stub_config
    else:
        # Run sample in standalone mode
        server, username, password, cleardata, skip_verification, vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])
        stub_config = vapiconnect.connect(server,
                                          username,
                                          password,
                                          skip_verification)
        atexit.register(vapiconnect.logout, stub_config)


def run():
    # Get a placement spec
    datacenter_name = testbed.config['DATACENTER2_NAME']
    vm_folder_name = testbed.config['VM_FOLDER2_NAME']
    datastore_name = testbed.config['NFS_DATASTORE_NAME']
    placement_spec = vm_placement_helper.get_placement_spec_for_resource_pool(
        stub_config,
        datacenter_name,
        vm_folder_name,
        datastore_name)

    # Create the VMs
    create_default_vm(stub_config, placement_spec)


def create_default_vm(stub_config, placement_spec):
    """
    Create a default VM.

    Using the provided PlacementSpec, create a VM with a selected Guest OS
    and provided name.  Use all the guest and system provided defaults.
    """
    guest_os = testbed.config['VM_GUESTOS']
    vm_create_spec = VM.CreateSpec(name=vm_name,
                                   guest_os=guest_os,
                                   placement=placement_spec)
    print('\n# Example: create_default_vm: Creating a VM using spec\n-----')
    print(pp(vm_create_spec))
    print('-----')

    vm_svc = VM(stub_config)
    vm = vm_svc.create(vm_create_spec)
    print("create_default_vm: Created VM '{}' ({})".format(vm_name, vm))

    vm_info = vm_svc.get(vm)
    print('vm.get({}) -> {}'.format(vm, pp(vm_info)))
    return vm


def cleanup():
    vm = get_vm(stub_config, vm_name)
    if vm:
        power_svc = Power(stub_config)
        vm_svc = VM(stub_config)
        state = power_svc.get(vm)
        if state == Power.Info(state=Power.State.POWERED_ON):
            power_svc.stop(vm)
        elif state == Power.Info(state=Power.State.SUSPENDED):
            power_svc.start(vm)
            power_svc.stop(vm)
        print("Deleting VM '{}' ({})".format(vm_name, vm))
        vm_svc.delete(vm)


def main():
    setup()
    cleanup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
