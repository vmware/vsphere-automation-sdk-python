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

from com.vmware.vcenter.vm_client import (Power)
from com.vmware.vcenter_client import VM

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.sample_util import pp
from samples.vsphere.common.service_manager import ServiceManager
from samples.vsphere.vcenter.helper import vm_placement_helper
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.vcenter.setup import testbed


class CreateDefaultVM(object):
    """
    Demonstrates how to create a VM with system provided defaults

    Sample Prerequisites:
        - datacenter
        - vm folder
        - datastore
    """

    def __init__(self, stub_config=None, placement_spec=None):
        self.context = None
        self.service_manager = None
        self.stub_config = stub_config
        self.placement_spec = placement_spec
        self.vm_name = testbed.config['VM_NAME_DEFAULT']
        self.cleardata = None

    def setup(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            help='Name of the testing vm')
        args = sample_util.process_cli_args(parser.parse_args())
        if args.vm_name:
            self.vm_name = args.vm_name
        self.cleardata = args.cleardata

        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

        self.stub_config = self.service_manager.stub_config

    def run(self):
        # Get a placement spec
        datacenter_name = testbed.config['VM_DATACENTER_NAME']
        vm_folder_name = testbed.config['VM_FOLDER2_NAME']
        datastore_name = testbed.config['VM_DATASTORE_NAME']

        if not self.placement_spec:
            self.placement_spec = vm_placement_helper.get_placement_spec_for_resource_pool(
                self.stub_config,
                datacenter_name,
                vm_folder_name,
                datastore_name)

        """
        Create a default VM.

        Using the provided PlacementSpec, create a VM with a selected Guest OS
        and provided name.  Use all the guest and system provided defaults.
        """
        guest_os = testbed.config['VM_GUESTOS']
        vm_create_spec = VM.CreateSpec(name=self.vm_name,
                                       guest_os=guest_os,
                                       placement=self.placement_spec)
        print('\n# Example: create_default_vm: Creating a VM using spec\n-----')
        print(pp(vm_create_spec))
        print('-----')

        vm_svc = VM(self.stub_config)
        vm = vm_svc.create(vm_create_spec)
        print("create_default_vm: Created VM '{}' ({})".format(self.vm_name, vm))

        vm_info = vm_svc.get(vm)
        print('vm.get({}) -> {}'.format(vm, pp(vm_info)))
        return vm

    def cleanup(self):
        vm = get_vm(self.stub_config, self.vm_name)
        if vm:
            power_svc = Power(self.stub_config)
            vm_svc = VM(self.stub_config)
            state = power_svc.get(vm)
            if state == Power.Info(state=Power.State.POWERED_ON):
                power_svc.stop(vm)
            elif state == Power.Info(state=Power.State.SUSPENDED):
                power_svc.start(vm)
                power_svc.stop(vm)
            print("Deleting VM '{}' ({})".format(self.vm_name, vm))
            vm_svc.delete(vm)


def main():
    create_default_vm = CreateDefaultVM()
    create_default_vm.setup()
    create_default_vm.cleanup()
    create_default_vm.run()
    if create_default_vm.cleardata:
        create_default_vm.cleanup()


if __name__ == '__main__':
    main()
