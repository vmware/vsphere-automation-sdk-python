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

from com.vmware.vcenter.vm_client import Power
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates the virtual machine power lifecycle

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
stub_config = None
vm_power_svc = None
cleardata = False


def setup(context=None):
    global stub_config, cleardata, vm_name
    if context:
        # Run sample suite via setup script
        vm_name = testbed.config['VM_NAME_DEFAULT']
        stub_config = context.stub_config
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
        raise Exception('Sample requires an existing vm with name ({}).'
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Power Sample".format(vm_name, vm))

    # Create Power stub used for making requests
    global vm_power_svc
    vm_power_svc = Power(stub_config)

    # Get the vm power state
    print('\n# Example: Get current vm power state')
    status = vm_power_svc.get(vm)
    print('vm.Power.get({}) -> {}'.format(vm, pp(status)))

    # Power off the vm if it is on
    if status == Power.Info(state=Power.State.POWERED_ON):
        print('\n# Example: VM is powered on, power it off')
        vm_power_svc.stop(vm)
        print('vm.Power.stop({})'.format(vm))

    # Power on the vm
    print('# Example: Power on the vm')
    vm_power_svc.start(vm)
    print('vm.Power.start({})'.format(vm))

    # Suspend the vm
    print('\n# Example: Suspend the vm')
    vm_power_svc.suspend(vm)
    print('vm.Power.suspend({})'.format(vm))

    # Resume the vm
    print('\n# Example: Resume the vm')
    vm_power_svc.start(vm)
    print('vm.Power.start({})'.format(vm))

    # Reset the vm
    print('\n# Example: Reset the vm')
    vm_power_svc.reset(vm)
    print('vm.Power.reset({})'.format(vm))


def cleanup():
    # Power off the vm
    print('\n# Cleanup: Power off the vm')
    vm_power_svc.stop(vm)
    print('vm.Power.stop({})'.format(vm))
    status = vm_power_svc.get(vm)
    if status == Power.Info(state=Power.State.POWERED_OFF,
                            clean_power_off=True):
        print('VM is powered off')
    else:
        print('vm.Power Warning: Could not power off vm')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
