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

from com.vmware.vcenter.vm.hardware.adapter_client import Sata
from com.vmware.vcenter.vm.hardware_client import (Cdrom,
                                                   IdeAddressSpec,
                                                   SataAddressSpec)
from com.vmware.vcenter.vm_client import Power
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to configure CD-ROM devices for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
sata = None
stub_config = None
cdrom_svc = None
vm_power_svc = None
sata_svc = None
cleardata = False
cdroms_to_delete = []
orig_cdrom_summaries = None


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
    print("Using VM '{}' ({}) for CD-ROM Sample".format(vm_name, vm))
    iso_datastore_path = testbed.config['ISO_DATASTORE_PATH']

    # Create CD-ROM stub used for making requests
    global cdrom_svc, vm_power_svc, sata_svc
    cdrom_svc = Cdrom(stub_config)
    vm_power_svc = Power(stub_config)

    # Create SATA controller
    print('\n# Setup: Create a SATA controller')
    sata_svc = Sata(stub_config)
    sata_create_spec = Sata.CreateSpec()
    print('# Adding SATA controller for SATA Disk samples')
    global sata
    sata = sata_svc.create(vm, sata_create_spec)
    print('vm.hardware.adapter.Sata.create({}, {}) -> {}'.
          format(vm, sata_create_spec, sata))

    print('\n# Example: List all Cdroms for a VM')
    cdrom_summaries = cdrom_svc.list(vm=vm)
    print('vm.hardware.Cdrom.list({}) -> {}'.format(vm, cdrom_summaries))

    # Save current list of Cdroms to verify that we have cleaned up properly
    global orig_cdrom_summaries
    orig_cdrom_summaries = cdrom_summaries

    # Get information for each CD-ROM on the VM
    for cdrom_summary in cdrom_summaries:
        cdrom = cdrom_summary.cdrom
        cdrom_info = cdrom_svc.get(vm=vm, cdrom=cdrom)
        print('vm.hardware.Cdrom.get({}, {}) -> {}'.
              format(vm, cdrom, pp(cdrom_info)))

    global cdroms_to_delete

    print('\n# Example: Create CD-ROM with ISO_FILE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        start_connected=True,
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.ISO_FILE,
                                  iso_file=iso_datastore_path))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create CD-ROM with CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create CD-ROM using auto-detect HOST_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.HOST_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create SATA CD-ROM using CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        type=Cdrom.HostBusAdapterType.SATA,
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create SATA CD-ROM on specific bus using '
          'CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        type=Cdrom.HostBusAdapterType.SATA,
        sata=SataAddressSpec(bus=0),
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create SATA CD-ROM on specific bus and unit using '
          'CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        type=Cdrom.HostBusAdapterType.SATA,
        sata=SataAddressSpec(bus=0, unit=10),
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create IDE CD-ROM using CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        type=Cdrom.HostBusAdapterType.IDE,
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Create IDE CD-ROM on specific bus and unit using '
          'CLIENT_DEVICE backing')
    cdrom_create_spec = Cdrom.CreateSpec(
        type=Cdrom.HostBusAdapterType.IDE,
        ide=IdeAddressSpec(False, True),
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.CLIENT_DEVICE))
    cdrom = cdrom_svc.create(vm, cdrom_create_spec)
    print('vm.hardware.Cdrom.create({}, {}) -> {}'.
          format(vm, cdrom_create_spec, cdrom))
    cdroms_to_delete.append(cdrom)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    # Change the last cdrom that was created

    print('\n# Example: Update backing from CLIENT_DEVICE to ISO_FILE')
    cdrom_update_spec = Cdrom.UpdateSpec(
        backing=Cdrom.BackingSpec(type=Cdrom.BackingType.ISO_FILE,
                                  iso_file=iso_datastore_path))
    print('vm.hardware.Cdrom.update({}, {}, {})'.
          format(vm, cdrom, cdrom_update_spec))
    cdrom_svc.update(vm, cdrom, cdrom_update_spec)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Update start_connected=False, '
          'allow_guest_control=False')
    cdrom_update_spec = Cdrom.UpdateSpec(
        start_connected=False, allow_guest_control=False)
    print('vm.hardware.Cdrom.update({}, {}, {})'.
          format(vm, cdrom, cdrom_update_spec))
    cdrom_svc.update(vm, cdrom, cdrom_update_spec)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.start(vm)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Connect CD-ROM after powering on VM')
    cdrom_svc.connect(vm, cdrom)
    print('vm.hardware.Cdrom.connect({}, {})'.format(vm, cdrom))
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Example: Disconnect CD-ROM while VM is powered on')
    cdrom_svc.disconnect(vm, cdrom)
    print('vm.hardware.Cdrom.disconnect({}, {})'.format(vm, cdrom))
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.stop(vm)
    cdrom_info = cdrom_svc.get(vm, cdrom)
    print('vm.hardware.Cdrom.get({}, {}) -> {}'.
          format(vm, cdrom, pp(cdrom_info)))

    # List all Cdroms for a VM
    cdrom_summaries = cdrom_svc.list(vm=vm)
    print('vm.hardware.Cdrom.list({}) -> {}'.format(vm, cdrom_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM Cdroms that were added')
    for cdrom in cdroms_to_delete:
        cdrom_svc.delete(vm, cdrom)
        print('vm.hardware.Cdrom.delete({}, {})'.format(vm, cdrom))

    print('\n# Cleanup: Remove SATA controller')
    print('vm.hardware.adapter.Sata.delete({}, {})'.format(vm, sata))
    sata_svc.delete(vm, sata)

    cdrom_summaries = cdrom_svc.list(vm)
    print('vm.hardware.Cdrom.list({}) -> {}'.format(vm, cdrom_summaries))
    if set(orig_cdrom_summaries) != set(cdrom_summaries):
        print('vm.hardware.Cdrom WARNING: '
              'Final CD-ROM info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
