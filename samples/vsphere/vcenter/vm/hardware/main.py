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

import samples.vsphere.vcenter.vm.hardware.adapter.sata
import samples.vsphere.vcenter.vm.hardware.adapter.scsi
import samples.vsphere.vcenter.vm.hardware.boot
import samples.vsphere.vcenter.vm.hardware.boot_device
import samples.vsphere.vcenter.vm.hardware.cdrom
import samples.vsphere.vcenter.vm.hardware.cpu
import samples.vsphere.vcenter.vm.hardware.disk
import samples.vsphere.vcenter.vm.hardware.ethernet
import samples.vsphere.vcenter.vm.hardware.floppy
import samples.vsphere.vcenter.vm.hardware.memory
import samples.vsphere.vcenter.vm.hardware.parallel
import samples.vsphere.vcenter.vm.hardware.serial
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm


def setup(context):
    print('Setup vcenter.vm.hardware Samples Started')
    samples.vsphere.vcenter.vm.hardware.cpu.setup(context)
    samples.vsphere.vcenter.vm.hardware.memory.setup(context)
    samples.vsphere.vcenter.vm.hardware.disk.setup(context)
    samples.vsphere.vcenter.vm.hardware.adapter.sata.setup(context)
    samples.vsphere.vcenter.vm.hardware.adapter.scsi.setup(context)
    samples.vsphere.vcenter.vm.hardware.boot.setup(context)
    samples.vsphere.vcenter.vm.hardware.boot_device.setup(context)
    samples.vsphere.vcenter.vm.hardware.cdrom.setup(context)
    samples.vsphere.vcenter.vm.hardware.ethernet.setup(context)
    samples.vsphere.vcenter.vm.hardware.floppy.setup(context)
    samples.vsphere.vcenter.vm.hardware.serial.setup(context)
    samples.vsphere.vcenter.vm.hardware.parallel.setup(context)
    print('Setup vcenter.vm.hardware Samples Complete\n')


def cleanup():
    print('Cleanup vcenter.vm.hardware Samples Started')
    samples.vsphere.vcenter.vm.hardware.cpu.cleanup()
    samples.vsphere.vcenter.vm.hardware.memory.cleanup()
    samples.vsphere.vcenter.vm.hardware.disk.cleanup()
    samples.vsphere.vcenter.vm.hardware.adapter.sata.cleanup()
    samples.vsphere.vcenter.vm.hardware.adapter.scsi.cleanup()
    samples.vsphere.vcenter.vm.hardware.boot.cleanup()
    samples.vsphere.vcenter.vm.hardware.boot_device.cleanup()
    samples.vsphere.vcenter.vm.hardware.cdrom.cleanup()
    samples.vsphere.vcenter.vm.hardware.ethernet.cleanup()
    samples.vsphere.vcenter.vm.hardware.floppy.cleanup()
    samples.vsphere.vcenter.vm.hardware.serial.cleanup()
    samples.vsphere.vcenter.vm.hardware.parallel.cleanup()
    print('Cleanup vcenter.vm.hardware Samples Complete\n')


def validate(context):
    print('Validating and Detecting Resources in vcenter.vm.hardware Samples')
    names = set([testbed.config['VM_NAME_DEFAULT'],
                 testbed.config['VM_NAME_BASIC'],
                 testbed.config['VM_NAME_EXHAUSTIVE']])
    valid = True
    for name in names:
        if not get_vm(context.client, name):
            valid = False
    if not valid:
        raise Exception('==> Samples Setup validation failed: '
                        'Missing VMs required to run hardware samples')
    print('==> Samples Setup validated')


def run():
    ###########################################################################
    # Incremental device CRUDE + connect/disconnect samples
    #
    # Choose any combination of the following incremental hardware examples.
    # Each one will return the VM to its original configuration.
    #
    # * CPU update sample
    # * Memory update sample
    # * Disk CRUD sample
    # * Ethernet CRUD sample
    # * CDROM CRUD sample
    # * SCSI adapter sample
    # * SATA adapter sample
    # * Serial Port CRUD sample
    # * Parallel Port CRUD sample
    # * Floppy CRUD sample
    # * Boot configuration sample
    # * Boot Device configuration sample
    ###########################################################################
    print('#' * 79)
    print('# vcenter.vm.hardware Samples')
    print('#' * 79)
    samples.vsphere.vcenter.vm.hardware.cpu.run()
    samples.vsphere.vcenter.vm.hardware.memory.run()
    samples.vsphere.vcenter.vm.hardware.disk.run()
    samples.vsphere.vcenter.vm.hardware.adapter.sata.run()
    samples.vsphere.vcenter.vm.hardware.adapter.scsi.run()
    samples.vsphere.vcenter.vm.hardware.boot.run()
    samples.vsphere.vcenter.vm.hardware.boot_device.run()
    samples.vsphere.vcenter.vm.hardware.cdrom.run()
    samples.vsphere.vcenter.vm.hardware.ethernet.run()
    samples.vsphere.vcenter.vm.hardware.floppy.run()
    samples.vsphere.vcenter.vm.hardware.serial.run()
    samples.vsphere.vcenter.vm.hardware.parallel.run()

    ###########################################################################
    # Virtual Hardware Upgrade Sample
    #
    # TODO Not implemented
    ###########################################################################

    ###########################################################################
    # Hot Add Samples
    # * Hot add disk
    # * Hot add cdrom
    # * ...
    # TODO Not implemented
    ###########################################################################
