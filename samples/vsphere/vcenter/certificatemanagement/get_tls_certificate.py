#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2020. All Rights Reserved.
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

import argparse
from samples.vsphere.common import (sample_cli, sample_util)
from vmware.vapi.vsphere.client import create_vsphere_client
import requests

"""
Description: Demonstrates retrieval of the MACHINE SSL certificate from the vCenter
along with the decoded X.509 certificate fields

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege.
"""

parser = sample_cli.build_arg_parser()

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

print('Listing the MACHINE SSL certificate along with the decoded X.509 fields ')
print(vsphere_client.vcenter.certificate_management.vcenter.Tls.get())
