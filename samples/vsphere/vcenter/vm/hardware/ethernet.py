#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
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

from com.vmware.vcenter.vm.hardware_client import Ethernet
from com.vmware.vcenter.vm_client import Power
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.helper import network_helper
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to configure virtual ethernet adapters of a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
stub_config = None
ethernet_svc = None
cleardata = False
nics_to_delete = []
orig_nic_summaries = None


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
    print("Using VM '{}' ({}) for Disk Sample".format(vm_name, vm))

    # Get standard portgroup to use as backing for sample
    standard_network = network_helper.get_standard_network_backing(
        stub_config,
        testbed.config['STDPORTGROUP_NAME'],
        testbed.config['VM_DATACENTER_NAME'])

    # Get distributed portgroup to use as backing for sample
    distributed_network = network_helper.get_distributed_network_backing(
        stub_config,
        testbed.config['VDPORTGROUP1_NAME'],
        testbed.config['VM_DATACENTER_NAME'])

    # Create Ethernet stub used for making requests
    global ethernet_svc
    ethernet_svc = Ethernet(stub_config)
    vm_power_svc = Power(stub_config)

    print('\n# Example: List all Ethernet adapters for a VM')
    nic_summaries = ethernet_svc.list(vm=vm)
    print('vm.hardware.Ethernet.list({}) -> {}'.format(vm, nic_summaries))

    # Save current list of Ethernet adapters to verify that we have cleaned
    # up properly
    global orig_nic_summaries
    orig_nic_summaries = nic_summaries

    # Get information for each Ethernet on the VM
    for nic_summary in nic_summaries:
        nic = nic_summary.nic
        nic_info = ethernet_svc.get(vm=vm, nic=nic)
        print('vm.hardware.Ethernet.get({}, {}) -> {}'.
              format(vm, nic, nic_info))

    global nics_to_delete

    print('\n# Example: Create Ethernet Nic using STANDARD_PORTGROUP with '
          'default settings')
    nic_create_spec = Ethernet.CreateSpec(
        backing=Ethernet.BackingSpec(
            type=Ethernet.BackingType.STANDARD_PORTGROUP,
            network=standard_network))
    nic = ethernet_svc.create(vm, nic_create_spec)
    print('vm.hardware.Ethernet.create({}, {}) -> {}'.
          format(vm, nic_create_spec, nic))
    nics_to_delete.append(nic)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Create Ethernet Nic using DISTRIBUTED_PORTGROUP '
          'with defaults')
    nic_create_spec = Ethernet.CreateSpec(
        backing=Ethernet.BackingSpec(
            type=Ethernet.BackingType.DISTRIBUTED_PORTGROUP,
            network=distributed_network))
    nic = ethernet_svc.create(vm, nic_create_spec)
    print('vm.hardware.Ethernet.create({}, {}) -> {}'.
          format(vm, nic_create_spec, nic))
    nics_to_delete.append(nic)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Create Ethernet Nic using STANDARD_'
          'PORTGROUP specifying')
    print('#          start_connected=True, allow_guest_control=True,')
    print('#          mac_type, mac_Address, wake_on_lan_enabled')
    nic_create_spec = Ethernet.CreateSpec(
        start_connected=True,
        allow_guest_control=True,
        mac_type=Ethernet.MacAddressType.MANUAL,
        mac_address='01:23:45:67:89:10',
        wake_on_lan_enabled=True,
        backing=Ethernet.BackingSpec(
            type=Ethernet.BackingType.STANDARD_PORTGROUP,
            network=standard_network))
    nic = ethernet_svc.create(vm, nic_create_spec)
    print('vm.hardware.Ethernet.create({}, {}) -> {}'.
          format(vm, nic_create_spec, nic))
    nics_to_delete.append(nic)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Create Ethernet Nic using DISTRIBUTED_PORTGROUP '
          'specifying')
    print('#          start_connected=True, allow_guest_control=True,')
    print('#          mac_type, mac_Address, wake_on_lan_enabled')
    nic_create_spec = Ethernet.CreateSpec(
        start_connected=True,
        allow_guest_control=True,
        mac_type=Ethernet.MacAddressType.MANUAL,
        mac_address='24:68:10:12:14:16',
        wake_on_lan_enabled=True,
        backing=Ethernet.BackingSpec(
            type=Ethernet.BackingType.DISTRIBUTED_PORTGROUP,
            network=distributed_network))
    nic = ethernet_svc.create(vm, nic_create_spec)
    print('vm.hardware.Ethernet.create({}, {}) -> {}'.
          format(vm, nic_create_spec, nic))
    nics_to_delete.append(nic)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    # Change the last nic that was created
    print('\n# Example: Update Ethernet Nic with different backing')
    nic_update_spec = Ethernet.UpdateSpec(
        backing=Ethernet.BackingSpec(
            type=Ethernet.BackingType.STANDARD_PORTGROUP,
            network=standard_network))
    print('vm.hardware.Ethernet.update({}, {}, {})'.
          format(vm, nic, nic_update_spec))
    ethernet_svc.update(vm, nic, nic_update_spec)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Update Ethernet Nic wake_on_lan_enabled=False')
    print('#                              mac_type=GENERATED,')
    print('#                              start_connected=False,')
    print('#                              allow_guest_control=False')
    nic_update_spec = Ethernet.UpdateSpec(
        wake_on_lan_enabled=False,
        mac_type=Ethernet.MacAddressType.GENERATED,
        start_connected=False,
        allow_guest_control=False)
    print('vm.hardware.Ethernet.update({}, {}, {})'.
          format(vm, nic, nic_update_spec))
    ethernet_svc.update(vm, nic, nic_update_spec)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.start(vm)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Connect Ethernet Nic after powering on VM')
    ethernet_svc.connect(vm, nic)
    print('vm.hardware.Ethernet.connect({}, {})'.format(vm, nic))
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Example: Disconnect Ethernet Nic while VM is powered on')
    ethernet_svc.disconnect(vm, nic)
    print('vm.hardware.Ethernet.disconnect({}, {})'.format(vm, nic))
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.stop(vm)
    nic_info = ethernet_svc.get(vm, nic)
    print('vm.hardware.Ethernet.get({}, {}) -> {}'.
          format(vm, nic, pp(nic_info)))

    # List all Nics for a VM
    nic_summaries = ethernet_svc.list(vm=vm)
    print('vm.hardware.Ethernet.list({}) -> {}'.format(vm, nic_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM Nics that were added')
    for nic in nics_to_delete:
        ethernet_svc.delete(vm, nic)
        print('vm.hardware.Ethernet.delete({}, {})'.format(vm, nic))

    nic_summaries = ethernet_svc.list(vm)
    print('vm.hardware.Ethernet.list({}) -> {}'.format(vm, nic_summaries))
    if set(orig_nic_summaries) != set(nic_summaries):
        print('vm.hardware.Ethernet WARNING: '
              'Final Nic info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
