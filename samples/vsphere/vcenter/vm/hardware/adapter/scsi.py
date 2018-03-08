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

from com.vmware.vcenter.vm.hardware.adapter_client import Scsi
from samples.vsphere.common.sample_util import pp, \
    parse_cli_args_vm
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure virtual SCSI adapters of a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
cleardata = False
scsis_to_delete = []
orig_scsi_summaries = None


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
    print("Using VM '{}' ({}) for SCSI Sample".format(vm_name, vm))

    print('\n# Example: List all SCSI adapters for a VM')
    scsi_summaries = client.vcenter.vm.hardware.adapter.Scsi.list(vm=vm)
    print('vm.hardware.adapter.Scsi.list({}) -> {}'.format(vm, scsi_summaries))

    # Save current list of SCSI adapters to verify that we have cleaned up
    # properly
    global orig_scsi_summaries
    orig_scsi_summaries = scsi_summaries

    # Get information for each SCSI adapter on the VM
    for scsi_summary in scsi_summaries:
        scsi = scsi_summary.adapter
        scsi_info = client.vcenter.vm.hardware.adapter.Scsi.get(vm=vm, adapter=scsi)
        print('vm.hardware.adapter.Scsi.get({}, {}) -> {}'.
              format(vm, scsi, pp(scsi_info)))

    global scsis_to_delete

    print('\n# Example: Create SCSI adapter with defaults')
    scsi_create_spec = Scsi.CreateSpec()
    scsi =  client.vcenter.vm.hardware.adapter.Scsi.create(vm, scsi_create_spec)
    print('vm.hardware.adapter.Scsi.create({}, {}) -> {}'.
          format(vm, scsi_create_spec, scsi))
    scsis_to_delete.append(scsi)
    scsi_info =  client.vcenter.vm.hardware.adapter.Scsi.get(vm, scsi)
    print('vm.hardware.adapter.Scsi.get({}, {}) -> {}'.
          format(vm, scsi, pp(scsi_info)))

    print('\n# Example: Create SCSI adapter with a specific bus '
          'and sharing=True')
    scsi_create_spec = Scsi.CreateSpec(bus=2,
                                       sharing=Scsi.Sharing.VIRTUAL)
    scsi = client.vcenter.vm.hardware.adapter.Scsi.create(vm, scsi_create_spec)
    print('vm.hardware.adapter.Scsi.create({}, {}) -> {}'.
          format(vm, scsi_create_spec, scsi))
    scsis_to_delete.append(scsi)
    scsi_info = client.vcenter.vm.hardware.adapter.Scsi.get(vm, scsi)
    print('vm.hardware.adapter.Scsi.get({}, {}) -> {}'.
          format(vm, scsi, pp(scsi_info)))

    print('\n# Example: Update SCSI adapter by setting sharing=False')
    scsi_update_spec = Scsi.UpdateSpec(sharing=Scsi.Sharing.NONE)
    client.vcenter.vm.hardware.adapter.Scsi.update(vm, scsi, scsi_update_spec)
    print('vm.hardware.adapter.Scsi.update({}, {}, {})'.
          format(vm, scsi, scsi_create_spec))
    scsi_info =  client.vcenter.vm.hardware.adapter.Scsi.get(vm, scsi)
    print('vm.hardware.adapter.Scsi.get({}, {}) -> {}'.
          format(vm, scsi, pp(scsi_info)))

    # List all SCSI adapters for a VM
    scsi_summaries = client.vcenter.vm.hardware.adapter.Scsi.list(vm=vm)
    print('vm.hardware.adapter.Scsi.list({}) -> {}'.format(vm, scsi_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM SCSI adapters that were added')
    for scsi in scsis_to_delete:
        client.vcenter.vm.hardware.adapter.Scsi.delete(vm, scsi)
        print('vm.hardware.adapter.Scsi.delete({}, {})'.format(vm, scsi))

    scsi_summaries = client.vcenter.vm.hardware.adapter.Scsi.list(vm)
    print('vm.hardware.adapter.Scsi.list({}) -> {}'.format(vm, scsi_summaries))
    if set(orig_scsi_summaries) != set(scsi_summaries):
        print('vm.hardware.adapter.Scsi WARNING: '
              'Final SCSI adapters info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
