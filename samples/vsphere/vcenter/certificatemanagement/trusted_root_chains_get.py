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
Description: Demonstrates the retrieval of the TRUSTED ROOT CHAIN corresponding to the provided alias

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--certalias',
                    help='The alias of the certificate chain which is to be retrieved.'
                         'All the published certificate chains will be retrieved if not provided')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

cert_alias = args.certalias

if cert_alias is not None:
    print('Retrieving the certificate chain corresponding to the alias ' + cert_alias)
    print(vsphere_client.vcenter.certificate_management.vcenter.TrustedRootChains.get(cert_alias))
else:
    print('Retrieving the all the published certificate chains imported to vCenter')
    cert_aliases = vsphere_client.vcenter.certificate_management.vcenter.TrustedRootChains.list()
    for alias in cert_aliases:
        print('Retrieving the certificate chain for the alias ' + alias.chain)
        print(vsphere_client.vcenter.certificate_management.vcenter.TrustedRootChains.get(alias.chain))
