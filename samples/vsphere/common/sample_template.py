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

import atexit

from com.vmware.vcenter_client import VM
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args


class Sample:
    """
    Demonstrates getting list of VMs present in vCenter

    Sample Prerequisites:
        - vCenter
    """

    def __init__(self):
        self.vm_service = None  # Service used by the sample code.
        self.cleardata = None

    def setup(self):
        server, username, password, cleardata, skip_verification = \
            parse_cli_args()
        stub_config = vapiconnect.connect(server, username, password,
                                          skip_verification)
        self.vm_service = VM(stub_config)
        self.cleardata = cleardata
        atexit.register(vapiconnect.logout, stub_config)

    def run(self):
        vms = self.vm_service.list()
        print(vms)

    def cleanup(self):
        if self.cleardata:
            pass


def main():
    sample = Sample()
    sample.setup()
    sample.run()
    sample.cleanup()


# Start program
if __name__ == '__main__':
    main()
