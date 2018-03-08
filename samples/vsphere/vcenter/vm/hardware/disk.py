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

import atexit
from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.vcenter.vm.hardware.adapter_client import Sata
from com.vmware.vcenter.vm.hardware_client import Disk
from com.vmware.vcenter.vm.hardware_client import (IdeAddressSpec,
                                                   SataAddressSpec,
                                                   ScsiAddressSpec)
from pyVim.connect import SmartConnect, Disconnect
from samples.vsphere.common.vim.vmdk import (create_vmdk, delete_vmdk, detect_vmdk)

from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vim.inventory import \
    (get_datacenter_for_datastore, get_datastore_mo)
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure disk settings for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
client = None
soap_stub = None
service_instance = None
cleardata = False
saved_disk_info = None
datacenter_mo = None
disks_to_delete = []
orig_disk_summaries = None


def setup(context=None):
    global client, service_instance, cleardata
    if context:
        # Run sample suite via setup script
        vm_name = testbed.config['VM_NAME_DEFAULT']
        client = context.client
        service_instance = context.service_instance
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

        # Connect to VIM API Endpoint on vCenter system
        context = None
        if skip_verification:
            context = get_unverified_context()
        service_instance = SmartConnect(host=server,
                                        user=username,
                                        pwd=password,
                                        sslContext=context)
        atexit.register(Disconnect, service_instance)

    global vm, datacenter_name, datastore_name
    global datastore_mo, datacenter_mo, datastore_root_path
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Disk Sample".format(vm_name, vm))

    # Get the datacenter and datastore managed objects to be able to create and
    # delete VMDKs, which are backings for a VM Disk.
    datacenter_name = testbed.config['VM_DATACENTER_NAME']
    datastore_name = testbed.config['VM_DATASTORE_NAME']
    datastore_mo = get_datastore_mo(client,
                                    service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    datacenter_mo = get_datacenter_for_datastore(datastore_mo)

    # The datastore_root_path is path in the datastore where the additional
    # VMDK files will be created for this sample.
    datastore_root_path = testbed.config['DISK_DATASTORE_ROOT_PATH']


def run():
    GiB = 1024 * 1024 * 1024

    print('\n# Example: List all Disks for a VM')
    disk_summaries = client.vcenter.vm.hardware.Disk.list(vm=vm)
    print('vm.hardware.Disk.list({}) -> {}'.format(vm, disk_summaries))

    # Save current list of disks to verify that we have cleaned up properly
    global orig_disk_summaries
    orig_disk_summaries = disk_summaries

    # Get information for each Disk on the VM
    for disk_summary in disk_summaries:
        disk = disk_summary.disk
        disk_info = client.vcenter.vm.hardware.Disk.get(vm=vm, disk=disk)
        print('vm.hardware.Disk.get({}, {}) -> {}'.
              format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new Disk using default settings')
    disk_create_spec = Disk.CreateSpec(new_vmdk=Disk.VmdkCreateSpec())
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    global disks_to_delete
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.
          format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new Disk specifying the capacity in bytes \n' +
          '# and that the flat format (ie. SeSparse format) should be used.')
    disk_create_spec = Disk.CreateSpec(
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new SCSI Disk')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.
          format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new SCSI Disk on a specific bus')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        scsi=ScsiAddressSpec(bus=0),
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print(
        '\n# Example: Create a new SCSI Disk on a specific bus and unit number')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        scsi=ScsiAddressSpec(bus=0, unit=10),
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a SATA controller')
    sata_create_spec = Sata.CreateSpec()
    print('# Adding SATA controller for SATA Disk')
    global sata
    sata = client.vcenter.vm.hardware.adapter.Sata.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))

    print('\n# Example: Create a new SATA disk')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SATA,
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new SATA disk on a specific bus')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SATA,
        sata=SataAddressSpec(bus=0),
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new SATA disk on a specific bus and specific '
          'unit')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SATA,
        sata=SataAddressSpec(bus=0, unit=20),
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.
          format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new IDE disk')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.IDE,
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Create a new IDE disk on a specific bus and '
          'specific unit')
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.IDE,
        ide=IdeAddressSpec(False, False),
        new_vmdk=Disk.VmdkCreateSpec(capacity=10 * GiB))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Attach an existing VMDK using the default bus and unit')
    datastore_path = datastore_root_path + '/attach-defaults.vmdk'
    delete_vmdk_if_exist(client, service_instance._stub, datacenter_name,
                         datastore_name, datastore_path)
    create_vmdk(service_instance, datacenter_mo, datastore_path)
    disk_create_spec = Disk.CreateSpec(
        backing=Disk.BackingSpec(type=Disk.BackingType.VMDK_FILE,
                                 vmdk_file=datastore_path))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Attach an existing VMDK as a SCSI disk')
    datastore_path = datastore_root_path + '/attach-scsi.vmdk'
    delete_vmdk_if_exist(client, service_instance._stub, datacenter_name,
                         datastore_name, datastore_path)
    create_vmdk(service_instance, datacenter_mo, datastore_path)

    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        backing=Disk.BackingSpec(type=Disk.BackingType.VMDK_FILE,
                                 vmdk_file=datastore_path))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.
          format(vm, disk, pp(disk_info)))

    print('\n# Example: Attach an existing VMDK as a SCSI disk '
          'to a specific bus')
    datastore_path = datastore_root_path + '/attach-scsi0.vmdk'
    delete_vmdk_if_exist(client, service_instance._stub, datacenter_name,
                         datastore_name, datastore_path)
    create_vmdk(service_instance, datacenter_mo, datastore_path)
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        scsi=ScsiAddressSpec(bus=0),
        backing=Disk.BackingSpec(type=Disk.BackingType.VMDK_FILE,
                                 vmdk_file=datastore_path))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    print('\n# Example: Attach an existing VMDK as a SCSI disk '
          'to a specific bus and specific unit')
    datastore_path = datastore_root_path + '/attach-scsi0:11.vmdk'
    delete_vmdk_if_exist(client, service_instance._stub, datacenter_name,
                         datastore_name, datastore_path)
    create_vmdk(service_instance, datacenter_mo, datastore_path)
    disk_create_spec = Disk.CreateSpec(
        type=Disk.HostBusAdapterType.SCSI,
        scsi=ScsiAddressSpec(bus=0, unit=11),
        backing=Disk.BackingSpec(type=Disk.BackingType.VMDK_FILE,
                                 vmdk_file=datastore_path))
    disk = client.vcenter.vm.hardware.Disk.create(vm=vm, spec=disk_create_spec)
    print('vm.hardware.Disk.create({}, {}) -> {}'.
          format(vm, disk_create_spec, disk))
    disks_to_delete.append(disk)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))

    # Samples to update operation to change backing
    # Save the disk_info so we can delete the VMDK
    global saved_disk_info
    saved_disk_info = disk_info
    print(
        '\n# Example: Change the backing of the last disk to a new VMDK file.')
    datastore_path = datastore_root_path + '/update-scsi0:11.vmdk'
    delete_vmdk_if_exist(client, service_instance._stub, datacenter_name,
                         datastore_name, datastore_path)
    create_vmdk(service_instance, datacenter_mo, datastore_path)
    disk_update_spec = Disk.UpdateSpec(
        backing=Disk.BackingSpec(type=Disk.BackingType.VMDK_FILE,
                                 vmdk_file=datastore_path))
    print('vm.hardware.Disk.update({}, {}, {})'.
          format(vm, disk, disk_update_spec))
    client.vcenter.vm.hardware.Disk.update(vm=vm, disk=disk, spec=disk_update_spec)
    disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
    print('vm.hardware.Disk.get({}, {}) -> {}'.format(vm, disk, pp(disk_info)))


def cleanup():
    # Clean up the saved disk from the update sample
    vmdk_file = saved_disk_info.backing.vmdk_file
    print("\n# Cleanup: Delete VMDK '{}'".format(vmdk_file))
    delete_vmdk(service_instance, datacenter_mo, vmdk_file)

    # List all Disks for a VM
    disk_summaries = client.vcenter.vm.hardware.Disk.list(vm=vm)
    print('vm.hardware.Disk.list({}) -> {}'.format(vm, disk_summaries))

    print('\n# Cleanup: Delete VM Disks that were added')
    for disk in disks_to_delete:
        disk_info = client.vcenter.vm.hardware.Disk.get(vm, disk)
        print('vm.hardware.Disk.get({}, {}) -> {}'.
              format(vm, disk, pp(disk_info)))
        vmdk_file = disk_info.backing.vmdk_file

        client.vcenter.vm.hardware.Disk.delete(vm, disk)
        print('vm.hardware.Disk.delete({}, {})'.format(vm, disk))

        print("\n# Cleanup: Delete VMDK '{}'".format(vmdk_file))
        delete_vmdk(service_instance, datacenter_mo, vmdk_file)

    print('\n# Cleanup: Remove SATA controller')
    print('vm.hardware.adapter.Sata.delete({}, {})'.format(vm, sata))
    client.vcenter.vm.hardware.adapter.Sata.delete(vm, sata)

    disk_summaries = client.vcenter.vm.hardware.Disk.list(vm)
    print('vm.hardware.Disk.list({}) -> {}'.format(vm, disk_summaries))
    if set(orig_disk_summaries) != set(disk_summaries):
        print(
            'vm.hardware.Disk WARNING: Final Disk info does not match original')


def delete_vmdk_if_exist(client, soap_stub, datacenter_name,
                         datastore_name, datastore_path):
    if detect_vmdk(client, soap_stub, datacenter_name,
                   datastore_name, datastore_path):
        print("Detected VMDK '{}' {}".format(datastore_name, datastore_path))
        delete_vmdk(service_instance, datacenter_mo, datastore_path)
        print("Deleted VMDK '{}'".format(datastore_path))


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
