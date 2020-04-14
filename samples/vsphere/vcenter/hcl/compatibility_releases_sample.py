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

from com.vmware.esx.hcl.hosts_client import CompatibilityReleases

from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.common import sample_cli, sample_util


class CompatibilityReleasesSample(object):
    """
     Sample demonstrating vCenter HCL Get Compatibility Releases Operation
     Sample Prerequisites:
     vCenter on linux platform
     The vCenter should have HCL DataStore(Compatibility Data) Populated
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-id', '--host',
                            required=True,
                            help='MOID of the source host for eg "host-13"')
        args = sample_util.process_cli_args(parser.parse_args())
        self.host_id = args.host
        config = get_configuration(args.server, args.username,
                                   args.password,
                                   args.skipverification)
        self.api_client = CompatibilityReleases(config)

    def run(self):
        """
        Invokes the HCL Compatibility Releases GET API to get list of available releases for the source ESXi host
        """
        releases_info = self.api_client.list(self.host_id)
        print("Compatibility Releases Info : ", releases_info)


def main():
    """
     Entry point for the CompatibilityReleasesSample client
    """
    releasesSample = CompatibilityReleasesSample()
    releasesSample.run()


if __name__ == '__main__':
    main()
