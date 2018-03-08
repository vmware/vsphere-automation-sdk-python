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

from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.vcenter.vm.hardware_client import Cpu
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure CPU settings for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
cleardata = False
orig_cpu_info = None


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
    print("Using VM '{}' ({}) for Cpu Sample".format(vm_name, vm))

    print('\n# Example: Get current Cpu configuration')
    cpu_info = client.vcenter.vm.hardware.Cpu.get(vm)
    print('vm.hardware.Cpu.get({}) -> {}'.format(vm, pp(cpu_info)))

    # Save current Cpu info to verify that we have cleaned up properly
    global orig_cpu_info
    orig_cpu_info = cpu_info

    print('\n# Example: Update cpu field of Cpu configuration')
    update_spec = Cpu.UpdateSpec(count=2)
    print('vm.hardware.Cpu.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Cpu.update(vm, update_spec)

    # Get new Cpu configuration
    cpu_info = client.vcenter.vm.hardware.Cpu.get(vm)
    print('vm.hardware.Cpu.get({}) -> {}'.format(vm, pp(cpu_info)))

    print('\n# Example: Update other less likely used fields of Cpu configuration')
    update_spec = Cpu.UpdateSpec(cores_per_socket=2, hot_add_enabled=True)
    print('vm.hardware.Cpu.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Cpu.update(vm, update_spec)

    # Get new Cpu configuration
    cpu_info = client.vcenter.vm.hardware.Cpu.get(vm)
    print('vm.hardware.Cpu.get({}) -> {}'.format(vm, pp(cpu_info)))


def cleanup():
    print('\n# Cleanup: Revert Cpu configuration')
    update_spec = \
        Cpu.UpdateSpec(count=orig_cpu_info.count,
                       cores_per_socket=orig_cpu_info.cores_per_socket,
                       hot_add_enabled=orig_cpu_info.hot_add_enabled,
                       hot_remove_enabled=orig_cpu_info.hot_remove_enabled)
    print('vm.hardware.Cpu.update({}, {})'.format(vm, update_spec))
    client.vcenter.vm.hardware.Cpu.update(vm, update_spec)

    # Get final Cpu configuration
    cpu_info = client.vcenter.vm.hardware.Cpu.get(vm)
    print('vm.hardware.Cpu.get({}) -> {}'.format(vm, pp(cpu_info)))

    if cpu_info != orig_cpu_info:
        print('vm.hardware.Cpu WARNING: Final Cpu info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
