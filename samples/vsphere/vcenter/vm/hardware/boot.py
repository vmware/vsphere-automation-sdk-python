#!/usr/bin/env python

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

import atexit

from com.vmware.vcenter.vm.hardware_client import Boot
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed

from samples.vsphere.vcenter.helper.vm_helper import get_vm

"""
Demonstrates how to configure the settings used when booting a virtual machine.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
stub_config = None
boot_svc = None
cleardata = False
orig_boot_info = None


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
    print("Using VM '{}' ({}) for Boot Sample".format(vm_name, vm))

    # Create Boot stub used for making requests
    global boot_svc
    boot_svc = Boot(stub_config)

    print('\n# Example: Get current Boot configuration')
    boot_info = boot_svc.get(vm)
    print('vm.hardware.Boot.get({}) -> {}'.format(vm, pp(boot_info)))

    # Save current Boot info to verify that we have cleaned up properly
    global orig_boot_info
    orig_boot_info = boot_info

    print('\n# Example: Update firmware to EFI for Boot configuration')
    update_spec = Boot.UpdateSpec(type=Boot.Type.EFI)
    print('vm.hardware.Boot.update({}, {})'.format(vm, update_spec))
    boot_svc.update(vm, update_spec)
    boot_info = boot_svc.get(vm)
    print('vm.hardware.Boot.get({}) -> {}'.format(vm, pp(boot_info)))

    print('\n# Example: Update boot firmware to tell it to enter setup mode on '
          'next boot')
    update_spec = Boot.UpdateSpec(enter_setup_mode=True)
    print('vm.hardware.Boot.update({}, {})'.format(vm, update_spec))
    boot_svc.update(vm, update_spec)
    boot_info = boot_svc.get(vm)
    print('vm.hardware.Boot.get({}) -> {}'.format(vm, pp(boot_info)))

    print('\n# Example: Update boot firmware to introduce a delay in boot'
          ' process and to reboot')
    print('# automatically after a failure to boot. '
          '(delay=10000 ms, retry=True,')
    print('# retry_delay=30000 ms')
    update_spec = Boot.UpdateSpec(delay=10000,
                                  retry=True,
                                  retry_delay=30000)
    print('vm.hardware.Boot.update({}, {})'.format(vm, update_spec))
    boot_svc.update(vm, update_spec)
    boot_info = boot_svc.get(vm)
    print('vm.hardware.Boot.get({}) -> {}'.format(vm, pp(boot_info)))


def cleanup():
    print('\n# Cleanup: Revert Boot configuration')
    update_spec = \
        Boot.UpdateSpec(type=orig_boot_info.type,
                        efi_legacy_boot=orig_boot_info.efi_legacy_boot,
                        network_protocol=orig_boot_info.network_protocol,
                        delay=orig_boot_info.delay,
                        retry=orig_boot_info.retry,
                        retry_delay=orig_boot_info.retry_delay,
                        enter_setup_mode=orig_boot_info.enter_setup_mode)
    print('vm.hardware.Boot.update({}, {})'.format(vm, update_spec))
    boot_svc.update(vm, update_spec)
    boot_info = boot_svc.get(vm)
    print('vm.hardware.Boot.get({}) -> {}'.format(vm, pp(boot_info)))

    if boot_info != orig_boot_info:
        print('vm.hardware.Boot WARNING: '
              'Final Boot info does not match original')


def main():
    setup()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
