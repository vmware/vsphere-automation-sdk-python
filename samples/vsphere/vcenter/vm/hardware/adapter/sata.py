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

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm.hardware.adapter_client import Sata
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import pp, \
    parse_cli_args_vm
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to configure virtual SATA adapters of a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
stub_config = None
sata_svc = None
cleardata = False
satas_to_delete = []
orig_sata_summaries = None


def setup(context=None):
    global vm, vm_name, stub_config, cleardata
    if context:
        # Run sample suite via setup script
        stub_config = context.stub_config
        vm_name = testbed.config['VM_NAME_DEFAULT']
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
    global vm
    vm = get_vm(stub_config, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for SATA Sample".format(vm_name, vm))

    # Create SATA adapter stub used for making requests
    global sata_svc
    sata_svc = Sata(stub_config)

    print('\n# Example: List all SATA adapters for a VM')
    sata_summaries = sata_svc.list(vm=vm)
    print('vm.hardware.adapter.Sata.list({}) -> {}'.format(vm, sata_summaries))

    # Save current list of SATA adapters to verify that we have cleaned up
    # properly
    global orig_sata_summaries
    orig_sata_summaries = sata_summaries

    # Get information for each SATA adapter on the VM
    for sata_summary in sata_summaries:
        sata = sata_summary.adapter
        sata_info = sata_svc.get(vm=vm, adapter=sata)
        print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
              format(vm, sata, pp(sata_info)))

    global satas_to_delete

    print('\n# Example: Create SATA adapter with defaults')
    sata_create_spec = Sata.CreateSpec()
    sata = sata_svc.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))
    satas_to_delete.append(sata)
    sata_info = sata_svc.get(vm, sata)
    print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
          format(vm, sata, pp(sata_info)))

    print('\n# Example: Create SATA adapter with a specific bus')
    sata_create_spec = Sata.CreateSpec(bus=2)
    sata = sata_svc.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))
    satas_to_delete.append(sata)
    sata_info = sata_svc.get(vm, sata)
    print('vm.hardware.adapter.Sata.get({}, {}) -> {}'.
          format(vm, sata, pp(sata_info)))

    # List all SATA adapters for a VM
    sata_summaries = sata_svc.list(vm=vm)
    print('vm.hardware.adapter.Sata.list({}) -> {}'.format(vm, sata_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM SATA adapters that were added')
    for sata in satas_to_delete:
        sata_svc.delete(vm, sata)
        print('vm.hardware.adapter.Sata.delete({}, {})'.format(vm, sata))

    sata_summaries = sata_svc.list(vm)
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
