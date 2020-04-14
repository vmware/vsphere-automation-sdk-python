#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019-2020. All Rights Reserved.
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

from com.vmware.vcenter.lcm_client import Reports

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration


class SampleLcm(object):
    """
     Sample demonstrating vCenter LCM Update APIs
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-f', '--file_name',
                        help='Provide csv report file name.')
        args = sample_util.process_cli_args(parser.parse_args())
        self.csv_report = args.file_name
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.report_client = Reports(stub_config)

    def run(self):
        """
        Access to download the interop report APIs by providing csv_report name
        """
        report_details = self.report_client.get(self.csv_report)
        print("Report Details - ", report_details)


def main():
    """
     Entry point for the sample client
    """
    lcm = SampleLcm()
    lcm.run()


if __name__ == '__main__':
    main()
