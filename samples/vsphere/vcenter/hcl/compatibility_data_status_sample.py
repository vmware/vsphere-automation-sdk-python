#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
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
__vcenter_version__ = '7.0+'

from com.vmware.esx.hcl_client import CompatibilityData

from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.common import sample_cli, sample_util


class CompatibilityDataStatusSample(object):
    """
     Sample demonstrating vCenter HCL Compatibility Data Status Check Operation
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        config = get_configuration(args.server, args.username,
                                         args.password,
                                         args.skipverification)
        self.api_client = CompatibilityData(config)

    def run(self):
        """
        Invokes the HCL Compatibility Data Status GET API to get information
        about when the compatibility data was last updated
        """
        data_status_info = self.api_client.get()
        print("Compatibility Data Status : ", data_status_info)


def main():
    """
     Entry point for the CompatibilityDataStatusSample client
    """
    dataStatusSample = CompatibilityDataStatusSample()
    dataStatusSample.run()


if __name__ == '__main__':
    main()
