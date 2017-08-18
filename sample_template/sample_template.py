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

__author__ = 'TODO: <your name and email>'
__vcenter_version__ = 'TODO: <compatible vcenter versions>'

import atexit

from com.vmware.vcenter_client import VM
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.service_manager import ServiceManager


class Sample(object):
    """
    TODO: Sample description and prerequisites.
    e.g. Demonstrates getting list of VMs present in vCenter

    Sample Prerequisites:
        - vCenter
    """

    def __init__(self):
        self.service_manager = None
        self.vm_name = None
        self.cleardata = None

    def setup(self):
        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification
        parser = sample_cli.build_arg_parser()

        # Add your custom input arguments
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            default='Sample_Default_VM_for_Simple_Testbed',
                            help='Name of the testing vm')

        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vm_name
        self.cleardata = args.cleardata

        # Connect to both Vim and vAPI services
        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

    def run(self):
        # TODO add your sample code here

        # Using REST API service
        vm_service = VM(self.service_manager.stub_config)
        filter_spec = VM.FilterSpec(names=set([self.vm_name]))
        vms = vm_service.list(filter_spec)
        print(vms)

        # Using Vim API service (pyVmomi)
        current_time = self.service_manager.si.CurrentTime()
        print(current_time)

    def cleanup(self):
        if self.cleardata:
            # TODO add cleanup code
            pass


def main():
    sample = Sample()
    sample.setup()
    sample.run()
    sample.cleanup()


if __name__ == '__main__':
    main()
