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
__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import VM
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common.service_manager_factory import ServiceManagerFactory


class Sample:
    """
    Demonstrates getting list of VMs present in vCenter

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
        service_manager = ServiceManagerFactory.get_service_manager(
            server,
            username,
            password,
            skip_verification)

        # Get the vAPI stub
        self.stub_config = service_manager.stub_config
        self.vm_service = VM(self.stub_config)

        # Get VIM service instance (pyVmomi)
        self.si = service_manager.si

    def run(self):
        vms = self.vm_service.list()
        print(vms)

        current_time = self.si.CurrentTime()
        print(current_time)

    def cleanup(self):
        if self.cleardata:
            pass


def main():
    sample = Sample()
    sample.setup()
    sample.run()
    sample.cleanup()


if __name__ == '__main__':
    main()
