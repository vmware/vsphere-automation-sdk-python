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

import samples.vsphere.vcenter.helper.network_helper
import samples.vsphere.vcenter.vm.hardware.main
import samples.vsphere.vcenter.vm.placement
import samples.vsphere.vcenter.vm.power
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed_setup
from samples.vsphere.vcenter.vm.create import create_basic_vm
from samples.vsphere.vcenter.vm.create import create_default_vm
from samples.vsphere.vcenter.vm.create import create_exhaustive_vm


def setup(context):
    print('Setup Samples Started')
    create_default_vm.setup(context)
    create_basic_vm.setup(context)
    create_exhaustive_vm.setup(context)
    print('Setup Samples Complete')


def cleanup(context):
    setup(context)

    print('Cleanup Samples Started')
    create_default_vm.cleanup()
    create_basic_vm.cleanup()
    create_exhaustive_vm.cleanup()
    print('Cleanup Samples Complete\n')


def validate(context):
    print('Validating and Detecting Resources in vcenter.vm Samples')
    r = testbed_setup.validate(context)
    if r:
        print('==> Samples Setup validated')
        return True
    else:
        print('==> Samples Setup has errors')
        return False


def run(context):
    # Clean up in case of past failures
    cleanup(context)

    # Check that sample is ready to run
    if context.option['DO_SAMPLES']:
        if not validate(context):
            exit(0)

    ###########################################################################
    # Getting a PlacementSpec
    ###########################################################################
    placement_spec = samples.vsphere.vcenter.vm.placement \
        .get_placement_spec_for_resource_pool(context)
    print('=' * 79)
    print('= Resource selection')
    print('=' * 79)
    print('placement_spec={}'.format(pp(placement_spec)))

    ###########################################################################
    # Getting a Network
    # Choose one of the following ways to get the PlacementSpec
    # 1. STANDARD_PORTGROUP on DATACENTER2
    # 2. DISTRIBUTED_PORTGROUP on DATACENTER2
    ###########################################################################
    standard_network = samples.vsphere.vcenter.helper \
        .network_helper.get_standard_network_backing(
        context.stub_config,
        context.testbed.config['STDPORTGROUP_NAME'],
        context.testbed.config['VM_DATACENTER_NAME'])
    print('standard_network={}'.format(standard_network))

    distributed_network = samples.vsphere.vcenter.helper \
        .network_helper.get_distributed_network_backing(
        context.stub_config,
        context.testbed.config['VDPORTGROUP1_NAME'],
        context.testbed.config['VM_DATACENTER_NAME'])
    print('distributed_network={}'.format(distributed_network))

    print('=' * 79)

    ###########################################################################
    # Create VM samples
    #
    # Choose one of the following ways to create the VM
    # 1. Default
    # 2. Basic (2 disks, 1 nic)
    # 3. Exhaustive (3 disks, 2 nics, 2 vcpu, 2 GB memory, boot=BIOS, 1 cdrom,
    #                1 serial port, 1 parallel port, 1 floppy,
    #                boot_devices= [CDROM, DISK, ETHERNET])
    ###########################################################################
    create_default_vm.create_default_vm(context.stub_config, placement_spec)
    create_basic_vm.create_basic_vm(context.stub_config,
                                    placement_spec,
                                    standard_network)
    create_exhaustive_vm.create_exhaustive_vm(context.stub_config,
                                              placement_spec,
                                              standard_network,
                                              distributed_network)

    ###########################################################################
    # Power operation samples
    #
    # Runs through the power lifecycle for the VM: start, suspend,
    # resume (start), stop
    #
    ###########################################################################
    samples.vsphere.vcenter.vm.power.setup(context)
    samples.vsphere.vcenter.vm.power.run()
    samples.vsphere.vcenter.vm.power.cleanup()

    ###########################################################################
    # Incremental device CRUDE + connect/disconnect samples
    #
    ###########################################################################
    if context.option['DO_SAMPLES_INCREMENTAL']:
        samples.vsphere.vcenter.vm.hardware.main.setup(context)
        samples.vsphere.vcenter.vm.hardware.main.validate(context)
        samples.vsphere.vcenter.vm.hardware.main.run()
        if context.option['DO_SAMPLES_CLEANUP']:
            samples.vsphere.vcenter.vm.hardware.main.cleanup()

    # Sample cleanup
    if context.option['DO_SAMPLES_CLEANUP']:
        cleanup(context)
