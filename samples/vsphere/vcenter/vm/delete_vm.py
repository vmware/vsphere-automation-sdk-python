#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm_client import Power
from com.vmware.vcenter_client import VM

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.service_manager import ServiceManager
from samples.vsphere.vcenter.helper.vm_helper import get_vm


class DeleteVM(object):
    """
    Demonstrates Deleting User specified Virtual Machine (VM)
    Sample Prerequisites:
    vCenter/ESX
    """

    def __init__(self):
        self.service_manager = None
        self.vm_name = None

    def setup(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            default='Sample_Default_VM_for_Simple_Testbed',
                            help='Name of the testing vm')
        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vm_name

        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

    def run(self):
        """
        Delete User specified VM from Server
        """
        vm_svc = VM(self.service_manager.stub_config)
        power_svc = Power(self.service_manager.stub_config)
        vm = get_vm(self.service_manager.stub_config, self.vm_name)
        if not vm:
            raise Exception('Sample requires an existing vm with name ({}).'
                            'Please create the vm first.'.format(vm_name))
        print("Deleting VM -- '{}-({})')".format(self.vm_name, vm))
        state = power_svc.get(vm)
        if state == Power.Info(state=Power.State.POWERED_ON):
            power_svc.stop(vm)
        elif state == Power.Info(state=Power.State.SUSPENDED):
            power_svc.start(vm)
            power_svc.stop(vm)
        vm_svc.delete(vm)
        print("Deleted VM -- '{}-({})".format(self.vm_name, vm))


def main():
    delete_vm = DeleteVM()
    delete_vm.setup()
    delete_vm.run()


if __name__ == '__main__':
    main()
