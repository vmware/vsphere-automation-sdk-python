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
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common.service_manager import ServiceManager


class Sample:
    """
    TODO: Sample description and prerequisites.
    e.g. Demonstrates getting list of VMs present in vCenter

    Sample Prerequisites:
        - vCenter
    """

    def __init__(self):
        self.vm_service = None  # Service used by the sample code.
        self.stub_config = None
        self.si = None
        self.cleardata = None

    def setup(self):
        server, username, password, cleardata, skip_verification = \
            parse_cli_args()
        self.cleardata = cleardata

        # Connect to both Vim and vAPI services
        service_manager = ServiceManager(server,
                                         username,
                                         password,
                                         skip_verification)
        service_manager.connect()
        atexit.register(service_manager.disconnect)

        # Get the vAPI stub
        self.stub_config = service_manager.stub_config
        self.vm_service = VM(self.stub_config)

        # Get VIM service instance (pyVmomi)
        self.si = service_manager.si

    def run(self):
        # TODO add steps to demo your API

        # Using vAPI services
        vms = self.vm_service.list()
        print(vms)

        # Using vim services
        current_time = self.si.CurrentTime()
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
