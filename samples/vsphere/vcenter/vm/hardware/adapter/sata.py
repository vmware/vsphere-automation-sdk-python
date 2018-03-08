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

from com.vmware.vcenter.vm.hardware.adapter_client import Sata
from samples.vsphere.common.sample_util import pp, \
    parse_cli_args_vm
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure virtual SATA adapters of a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
cleardata = False
satas_to_delete = []
orig_sata_summaries = None


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
    print("Using VM '{}' ({}) for SATA Sample".format(vm_name, vm))

    print('\n# Example: List all SATA adapters for a VM')
    sata_summaries = client.vcenter.vm.hardware.adapter.Sata.list(vm=vm)
    print('vm.hardware.adapter.Sata.list({}) -> {}'.format(vm, sata_summaries))

    # Save current list of SATA adapters to verify that we have cleaned up
    # properly
    global orig_sata_summaries
    orig_sata_summaries = sata_summaries

    # Get information for each SATA adapter on the VM
    for sata_summary in sata_summaries:
        sata = sata_summary.adapter
        sata_info = client.vcenter.vm.hardware.adapter.Sata.get(vm=vm, adapter=sata)
        print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
              format(vm, sata, pp(sata_info)))

    global satas_to_delete

    print('\n# Example: Create SATA adapter with defaults')
    sata_create_spec = Sata.CreateSpec()
    sata = client.vcenter.vm.hardware.adapter.Sata.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))
    satas_to_delete.append(sata)
    sata_info = client.vcenter.vm.hardware.adapter.Sata.get(vm, sata)
    print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
          format(vm, sata, pp(sata_info)))

    print('\n# Example: Create SATA adapter with a specific bus')
    sata_create_spec = Sata.CreateSpec(bus=2)
    sata = client.vcenter.vm.hardware.adapter.Sata.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))
    satas_to_delete.append(sata)
    sata_info = client.vcenter.vm.hardware.adapter.Sata.get(vm, sata)
    print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
          format(vm, sata, pp(sata_info)))

    # List all SATA adapters for a VM
    sata_summaries = client.vcenter.vm.hardware.adapter.Sata.list(vm=vm)
    print('vm.hardware.adapter.Sata.list({}) -> {}'.format(vm, sata_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM SATA adapters that were added')
    for sata in satas_to_delete:
        client.vcenter.vm.hardware.adapter.Sata.delete(vm, sata)
        print('vm.hardware.adapter.Sata.delete({}, {})'.format(vm, sata))

    sata_summaries = client.vcenter.vm.hardware.adapter.Sata.list(vm)
    print('vm.hardware.adapter.Sata.list({}) -> {}'.format(vm, sata_summaries))
    if set(orig_sata_summaries) != set(sata_summaries):
        print('vm.hardware.adapter.Sata WARNING: '
              'Final SATA adapters info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
