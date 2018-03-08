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

from com.vmware.vcenter.vm.hardware_client import Floppy
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure Floppy settings for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
floppy = None
client = None
cleardata = False
orig_floppy_summaries = None


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
    # * Floppy images must be pre-existing.  This API does not expose
    #   a way to create new floppy images.
    global vm
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Floppy Sample".format(vm_name, vm))
    img_datastore_path = testbed.config['FLOPPY_DATASTORE_PATH']

    print('\n# Example: List all Floppys for a VM')
    floppy_summaries = client.vcenter.vm.hardware.Floppy.list(vm=vm)
    print('vm.hardware.Floppy.list({}) -> {}'.format(vm, floppy_summaries))

    # Save current list of Floppys to verify that we have cleaned up properly
    global orig_floppy_summaries
    orig_floppy_summaries = floppy_summaries

    # Get information for each Floppy on the VM
    global floppy
    for floppy_summary in floppy_summaries:
        floppy = floppy_summary.floppy
        floppy_info = client.vcenter.vm.hardware.Floppy.get(vm=vm, floppy=floppy)
        print('vm.hardware.Floppy.get({}, {}) -> {}'.
              format(vm, floppy, pp(floppy_info)))

    # Maximum 2 Floppy devices allowed so delete them as they are created except
    # for the last one which will be deleted at the end

    print('\n# Example: Create Floppy port with defaults')
    floppy_create_spec = Floppy.CreateSpec()
    floppy = client.vcenter.vm.hardware.Floppy.create(vm, floppy_create_spec)
    print('vm.hardware.Floppy.create({}, {}) -> {}'.
          format(vm, floppy_create_spec, floppy))
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))
    client.vcenter.vm.hardware.Floppy.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    print('\n# Example: Create Floppy with CLIENT_DEVICE backing')
    floppy_create_spec = Floppy.CreateSpec(
        backing=Floppy.BackingSpec(type=Floppy.BackingType.CLIENT_DEVICE))
    floppy = client.vcenter.vm.hardware.Floppy.create(vm, floppy_create_spec)
    print('vm.hardware.Floppy.create({}, {}) -> {}'.
          format(vm, floppy_create_spec, floppy))
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))
    client.vcenter.vm.hardware.Floppy.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    print('\n# Example: Create Floppy with IMAGE_FILE backing, '
          'start_connected=True,')
    print('           allow_guest_control=True')
    floppy_create_spec = Floppy.CreateSpec(
        allow_guest_control=True,
        start_connected=True,
        backing=Floppy.BackingSpec(type=Floppy.BackingType.IMAGE_FILE,
                                   image_file=img_datastore_path))
    floppy = client.vcenter.vm.hardware.Floppy.create(vm, floppy_create_spec)
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Update start_connected=False, '
          'allow_guest_control=False')
    floppy_update_spec = Floppy.UpdateSpec(
        start_connected=False, allow_guest_control=False)
    print('vm.hardware.Floppy.update({}, {}, {})'.
          format(vm, floppy, floppy_update_spec))
    client.vcenter.vm.hardware.Floppy.update(vm, floppy, floppy_update_spec)
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.start(vm)
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Connect Floppy after powering on VM')
    client.vcenter.vm.hardware.Floppy.connect(vm, floppy)
    print('vm.hardware.Floppy.connect({}, {})'.format(vm, floppy))
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Example: Disconnect Floppy while VM is powered on')
    client.vcenter.vm.hardware.Floppy.disconnect(vm, floppy)
    print('vm.hardware.Floppy.disconnect({}, {})'.format(vm, floppy))
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.stop(vm)
    floppy_info = client.vcenter.vm.hardware.Floppy.get(vm, floppy)
    print('vm.hardware.Floppy.get({}, {}) -> {}'.
          format(vm, floppy, pp(floppy_info)))

    # List all Floppys for a VM
    floppy_summaries = client.vcenter.vm.hardware.Floppy.list(vm=vm)
    print('vm.hardware.Floppy.list({}) -> {}'.format(vm, floppy_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM Floppys that were added')
    client.vcenter.vm.hardware.Floppy.delete(vm, floppy)
    print('vm.hardware.Floppy.delete({}, {})'.format(vm, floppy))

    floppy_summaries = client.vcenter.vm.hardware.Floppy.list(vm)
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
