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

from com.vmware.vcenter.vm.hardware.boot_client import Device as BootDevice
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to modify the boot devices used by a virtual machine, and in
what order they are tried.

Sample Prerequisites:
The sample needs an existing VM with the following configuration:
    1 Ethernet adapter
    1 Cdrom
    1 Floppy drive
    3 Disks
"""

vm = None
vm_name = None
client = None
cleardata = False
orig_boot_device_entries = None


def setup(context=None):
    global vm, vm_name, client, cleardata
    if context:
        # Run sample suite via setup script
        client = context.client
        vm_name = testbed.config['VM_NAME_EXHAUSTIVE']
    else:
        # Run sample in standalone mode
        server, username, password, cleardata, skip_verification, vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_EXHAUSTIVE'])
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
    print("Using VM '{}' ({}) for BootDevice Sample".format(vm_name, vm))

    print('\n# Example: Get current BootDevice configuration')
    boot_device_entries = client.vcenter.vm.hardware.boot.Device.get(vm)
    print('vm.hardware.boot.Device.get({}) -> {}'.
          format(vm, pp(boot_device_entries)))

    # Save current BootDevice info to verify that we have cleaned up properly
    global orig_boot_device_entries
    orig_boot_device_entries = boot_device_entries

    # Get device identifiers for Disks
    disk_summaries = client.vcenter.vm.hardware.Disk.list(vm)
    print('vm.hardware.Disk.list({}) -> {}'.format(vm, pp(disk_summaries)))
    disks = [disk_summary.disk for disk_summary in disk_summaries]

    # Get device identifiers for Ethernet nics
    nic_summaries = client.vcenter.vm.hardware.Ethernet.list(vm)
    print('vm.hardware.Ethernet.list({}) -> {}'.format(vm, pp(nic_summaries)))
    nics = [nic_summary.nic for nic_summary in nic_summaries]

    print('\n# Example: Set Boot Order to be Floppy, '
          'Disk1, Disk2, Disk3, Cdrom,')
    print('#          Network (nic0), Network (nic1).')
    boot_device_entries = [
        BootDevice.Entry(BootDevice.Type.FLOPPY),
        BootDevice.Entry(BootDevice.Type.DISK, disks=disks),
        BootDevice.Entry(BootDevice.Type.CDROM)]
    for nic in nics:
        boot_device_entries.append(
            BootDevice.Entry(BootDevice.Type.ETHERNET, nic=nic))
    print('vm.hardware.boot.Device.set({}, {})'.format(vm, boot_device_entries))
    client.vcenter.vm.hardware.boot.Device.set(vm, boot_device_entries)
    boot_device_entries = client.vcenter.vm.hardware.boot.Device.get(vm)
    print('vm.hardware.boot.Device.get({}) -> {}'.
          format(vm, pp(boot_device_entries)))


def cleanup():
    print('\n# Cleanup: Revert BootDevice configuration')
    boot_device_entries = orig_boot_device_entries
    print('vm.hardware.boot.Device.set({}, {})'.format(vm, boot_device_entries))
    client.vcenter.vm.hardware.boot.Device.set(vm, boot_device_entries)
    boot_device_entries = client.vcenter.vm.hardware.boot.Device.get(vm)
    print('vm.hardware.boot.Device.get({}) -> {}'.
          format(vm, pp(boot_device_entries)))

    if boot_device_entries != orig_boot_device_entries:
        print('vm.hardware.boot.Device WARNING: '
              'Final BootDevice info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
