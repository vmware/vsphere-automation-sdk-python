#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm.hardware_client import Floppy
from com.vmware.vcenter.vm_client import Power
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to configure Floppy settings for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
floppy = None
stub_config = None
cleardata = False
orig_floppy_summaries = None


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
    # * Floppy images must be pre-existing.  This API does not expose
    #   a way to create new floppy images.
    global vm
    vm = get_vm(stub_config, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Floppy Sample".format(vm_name, vm))
    img_datastore_path = testbed.config['FLOPPY_DATASTORE_PATH']

    # Create Floppy stub used for making requests
    global floppy_svc
    floppy_svc = Floppy(stub_config)
    vm_power_svc = Power(stub_config)

    print('\n# Example: List all Floppys for a VM')
    floppy_summaries = floppy_svc.list(vm=vm)
    print('vm.hardware.Floppy.list({}) -> {}'.format(vm, floppy_summaries))

    # Save current list of Floppys to verify that we have cleaned up properly
    global orig_floppy_summaries
    orig_floppy_summaries = floppy_summaries

    # Get information for each Floppy on the VM
    global floppy
    for floppy_summary in floppy_summaries:
        floppy = floppy_summary.floppy
        floppy_info = floppy_svc.get(vm=vm, floppy=floppy)
        print('vm.hardware.Floppy.get({}, {}) -> {}'.
              format(vm, floppy, pp(floppy_info)))

    # Maximum 2 Floppy devices allowed so delete them as they are created except
    # for the last one which will be deleted at the end

    print('\n# Example: Create Floppy port with defaults')
    floppy_create_spec = Floppy.CreateSpec()
    floppy = floppy_svc.create(vm, floppy_create_spec)
    print('vm.hardware.Floppy.create({}, {}) -> {}'.
          format(vm, floppy_create_spec, floppy))
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))
    floppy_svc.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    print('\n# Example: Create Floppy with CLIENT_DEVICE backing')
    floppy_create_spec = Floppy.CreateSpec(
        backing=Floppy.BackingSpec(type=Floppy.BackingType.CLIENT_DEVICE))
    floppy = floppy_svc.create(vm, floppy_create_spec)
    print('vm.hardware.Floppy.create({}, {}) -> {}'.
          format(vm, floppy_create_spec, floppy))
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))
    floppy_svc.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    print('\n# Example: Create Floppy with IMAGE_FILE backing, '
          'start_connected=True,')
    print('           allow_guest_control=True')
    floppy_create_spec = Floppy.CreateSpec(
        allow_guest_control=True,
        start_connected=True,
        backing=Floppy.BackingSpec(type=Floppy.BackingType.IMAGE_FILE,
                                   image_file=img_datastore_path))
    floppy = floppy_svc.create(vm, floppy_create_spec)
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Update start_connected=False, '
          'allow_guest_control=False')
    floppy_update_spec = Floppy.UpdateSpec(
        start_connected=False, allow_guest_control=False)
    print('vm.hardware.Floppy.update({}, {}, {})'.
          format(vm, floppy, floppy_update_spec))
    floppy_svc.update(vm, floppy, floppy_update_spec)
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.start(vm)
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Connect Floppy after powering on VM')
    floppy_svc.connect(vm, floppy)
    print('vm.hardware.Floppy.connect({}, {})'.format(vm, floppy))
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Disconnect Floppy while VM is powered on')
    floppy_svc.disconnect(vm, floppy)
    print('vm.hardware.Floppy.disconnect({}, {})'.format(vm, floppy))
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.stop(vm)
    floppy_info = floppy_svc.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    # List all Floppys for a VM
    floppy_summaries = floppy_svc.list(vm=vm)
    print('vm.hardware.Floppy.list({}) -> {}'.format(vm, floppy_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM Floppys that were added')
    floppy_svc.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    floppy_summaries = floppy_svc.list(vm)
    print('vm.hardware.Floppy.list({}) -> {}'.format(vm, floppy_summaries))
    if set(orig_floppy_summaries) != set(floppy_summaries):
        print('vm.hardware.Floppy WARNING: '
              'Final Floppy info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
