#!/usr/bin/env python

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

from com.vmware.vcenter.vm.hardware_client import Memory
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure the memory related settings of a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
cleardata = False
orig_memory_info = None


def setup(context=None):
    global vm, vm_name, client, cleardata
    if context:
        # Run sample suite via setup script
        client = context.client
        vm_name = testbed.config['VM_NAME_DEFAULT']
    else:
        # Run sample in standalone mode
        server, username, password, cleardata, skip_verification, vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])
        session = get_unverified_session() if skip_verification else None

        # Connect to vSphere client
        client = create_vsphere_client(server=server,
                                       username=username,
                                       password=password,
                                       session=session)

def run():
    global vm
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Memory Sample".format(vm_name, vm))

    print('\n# Example: Get current Memory configuration')
    memory_info = client.vcenter.vm.hardware.Memory.get(vm)
    print('vm.hardware.Memory.get({}) -> {}'.format(vm, pp(memory_info)))

    # Save current Memory info to verify that we have cleaned up properly
    global orig_memory_info
    orig_memory_info = memory_info

    print('\n# Example: Update memory size_mib field of Memory configuration')
    update_spec = Memory.UpdateSpec(size_mib=8 * 1024)
    print('vm.hardware.Memory.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Memory.update(vm, update_spec)

    # Get new Memory configuration
    memory_info = client.vcenter.vm.hardware.Memory.get(vm)
    print('vm.hardware.Memory.get({}) -> {}'.format(vm, pp(memory_info)))

    print('\n# Example: Update hot_add_enabled field of Memory configuration')
    update_spec = Memory.UpdateSpec(hot_add_enabled=True)
    print('vm.hardware.Memory.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Memory.update(vm, update_spec)

    # Get new Memory configuration
    memory_info = client.vcenter.vm.hardware.Memory.get(vm)
    print('vm.hardware.Memory.get({}) -> {}'.format(vm, pp(memory_info)))


def cleanup():
    print('\n# Cleanup: Revert Memory configuration')
    update_spec = Memory.UpdateSpec(size_mib=orig_memory_info.size_mib,
                                    hot_add_enabled=orig_memory_info.
                                    hot_add_enabled)
    print('vm.hardware.Memory.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Memory.update(vm, update_spec)

    # Get final Memory configuration
    memory_info = client.vcenter.vm.hardware.Memory.get(vm)
    print('vm.hardware.Memory.get({}) -> {}'.format(vm, pp(memory_info)))

    if memory_info != orig_memory_info:
        print('vm.hardware.Memory WARNING: '
              'Final Memory info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
