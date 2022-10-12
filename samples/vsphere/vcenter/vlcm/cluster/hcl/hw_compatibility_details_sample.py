#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2022. All Rights Reserved.
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

from com.vmware.esx.settings.clusters.software.reports.hardware_compatibility_client import Details
from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.common import sample_util, sample_cli


class HWCompatibilityDetailsSample(object):
    """
     Sample demonstrating vCenter HCL Get HW Compatibility Details Operation
     Sample Prerequisites:
     vCenter on linux platform
     The vCenter should have HCL DataStore(Compatibility Data) Populated
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-id', '--cluster',
                            required=True,
                            help='MOID of the source cluster for eg "domain-c92"')
        args = sample_util.process_cli_args(parser.parse_args())
        self.cluster_id = args.cluster
        config = get_configuration(args.server, args.username,
                                   args.password,
                                   args.skipverification)

        self.api_client = Details(config)

    def run(self):
        """
        Access the HCL Hardware Compatibility Details GET API to get the task id
        """
        report_info = self.api_client.get(self.cluster_id)
        print("Hardware Compatibility Details : ", report_info)
        print("Storage Device Details: ", report_info.storage_device_compliance)
        print("PCI Device Details : ", report_info.pci_device_compliance)


def main():
    """
     Entry point for the CompatibilityReportSample client
    """
    detailsSample = HWCompatibilityDetailsSample()
    detailsSample.run()


if __name__ == '__main__':
    main()
