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

from com.vmware.vcenter.vm_client import Power
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session


"""
Demonstrates the virtual machine power lifecycle

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
cleardata = False


def setup(context=None):
    global client, cleardata, vm_name
    if context:
        # Run sample suite via setup script
        vm_name = testbed.config['VM_NAME_DEFAULT']
        client = context.client
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
    global vm
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}).'
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Power Sample".format(vm_name, vm))

    # Get the vm power state
    print('\n# Example: Get current vm power state')
    status = client.vcenter.vm.Power.get(vm)
    print('vm.Power.get({}) -> {}'.format(vm, pp(status)))

    # Power off the vm if it is on
    if status == Power.Info(state=Power.State.POWERED_ON):
        print('\n# Example: VM is powered on, power it off')
        client.vcenter.vm.Power.stop(vm)
        print('vm.Power.stop({})'.format(vm))

    # Power on the vm
    print('# Example: Power on the vm')
    client.vcenter.vm.Power.start(vm)
    print('vm.Power.start({})'.format(vm))

    # Suspend the vm
    print('\n# Example: Suspend the vm')
    client.vcenter.vm.Power.suspend(vm)
    print('vm.Power.suspend({})'.format(vm))

    # Resume the vm
    print('\n# Example: Resume the vm')
    client.vcenter.vm.Power.start(vm)
    print('vm.Power.start({})'.format(vm))

    # Reset the vm
    print('\n# Example: Reset the vm')
    client.vcenter.vm.Power.reset(vm)
    print('vm.Power.reset({})'.format(vm))


def cleanup():
    # Power off the vm
    print('\n# Cleanup: Power off the vm')
    client.vcenter.vm.Power.stop(vm)
    print('vm.Power.stop({})'.format(vm))
    status = client.vcenter.vm.Power.get(vm)
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
