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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter_client import VM

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.service_manager import ServiceManager
from pprint import pprint


class ListVM(object):
    """
    Demonstrates getting list of VMs present in vCenter
    Sample Prerequisites:
    vCenter/ESX
    """

    def __init__(self):
        self.service_manager = None

    def setup(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

    def run(self):
        """
        List VMs present in server
        """
        vm_svc = VM(self.service_manager.stub_config)
        list_of_vms = vm_svc.list()
        print("----------------------------")
        print("List Of VMs")
        print("----------------------------")
        pprint(list_of_vms)
        print("----------------------------")


def main():
    list_vm = ListVM()
    list_vm.setup()
    list_vm.run()


if __name__ == '__main__':
    main()
