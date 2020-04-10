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

from com.vmware.esx.hcl.hosts_client import CompatibilityReport

from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.common import sample_cli, sample_util


class CompatibilityReportSample(object):
    """
     Sample demonstrating vCenter HCL Get Compatibility Report Operation
     Sample Prerequisites:
     vCenter on linux platform
     The vCenter should have HCL DataStore(Compatibility Data) Populated
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-id', '--host',
                            required=True,
                            help='MOID of the source host for eg "host-13"')
        parser.add_argument('-r', '--release',
                            required=True,
                            help='Target Release against which you want to generate the report for eg "ESXi 6.7"')
        args = sample_util.process_cli_args(parser.parse_args())
        self.host_id = args.host
        self.targetRelease = args.release
        config = get_configuration(args.server, args.username,
                                   args.password,
                                   args.skipverification)
        self.api_client = CompatibilityReport(config)

    def run(self):
        """
        Access the HCL Compatibility Report GET API to get the task id
        """
        report_info = self.api_client.create_task(self.host_id,
                                         CompatibilityReport.Spec(self.targetRelease))
        print("Compatibility Report API Task ID : ", report_info.get_task_id())


def main():
    """
     Entry point for the CompatibilityReportSample client
    """
    reportSample = CompatibilityReportSample()
    reportSample.run()


if __name__ == '__main__':
    main()
