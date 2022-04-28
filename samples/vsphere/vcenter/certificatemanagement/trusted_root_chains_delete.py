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

from vmware.vapi.vsphere.client import create_vsphere_client
import requests
from com.vmware.vcenter.certificate_management.vcenter_client import TrustedRootChains
from samples.vsphere.common import (sample_cli, sample_util)

"""
Description: Demonstrates the deletion of the TRUSTED ROOT CHAIN corresponding to the provided alias

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Manage or the
CertificateManagement.Administer privilege
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--certalias',
                    required=True,
                    help='The alias for the certificate chain to be deleted from vCenter.')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

cert_alias = args.certalias

print('Deleting the certificate chain corresponding to the alias ' + cert_alias)
vsphere_client.vcenter.certificate_management.vcenter.TrustedRootChains.delete(cert_alias)
