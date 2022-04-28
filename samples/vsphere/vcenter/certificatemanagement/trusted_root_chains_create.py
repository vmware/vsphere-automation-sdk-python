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
from com.vmware.vcenter.certificate_management_client import X509CertChain
from samples.vsphere.common import (sample_cli, sample_util)

"""
Description: Demonstrates the import of the TRUSTED ROOT CHAIN into vCenter

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Manage or the
CertificateManagement.Administer privilege
"""

parser = sample_cli.build_arg_parser()


parser.add_argument('--certchain',
                    required=True,
                    help='The certificate chain to be imported into vCenter.')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

cert_chain = args.certchain.encode(encoding='utf-8').decode('unicode_escape').split(',')

"""
Creation of the spec for input to the API
"""
x509_cert_chain = X509CertChain(cert_chain=cert_chain)
cert_chain = TrustedRootChains.CreateSpec(cert_chain=x509_cert_chain)

print('The alias of the certificate chain successfully imported into vCenter listed below ')
print(vsphere_client.vcenter.certificate_management.vcenter.TrustedRootChains.create(cert_chain))
