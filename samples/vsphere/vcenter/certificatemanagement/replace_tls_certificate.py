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
from com.vmware.vcenter.certificate_management.vcenter_client import Tls
from samples.vsphere.common import (sample_cli, sample_util)

"""
Description: Demonstrates the replacement of the MACHINE SSL certificate with a custom
certificate signed by an external third party CA.

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Administer privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--cert',
                    required=True,
                    help='Leaf certificate for replace the MACHINE SSL certificate.')

parser.add_argument('--key',
                    help='The private key.'
                         'Not required if the gencsr api was used to generated the certificate signing request.')

parser.add_argument('--rootcert',
                    help='The root certificate and the intermediate root certificates '
                         'required to establish the chain of trust.'
                         'Not required if the certificates are already present in the vCenter.')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

cert = args.cert.encode(encoding='utf-8').decode('unicode_escape')

if args.key is not None:
    key = args.encode(encoding='utf-8').key.decode('unicode_escape')
else:
    key = args.key

if args.rootcert is not None:
    root_cert = args.rootcert.encode(encoding='utf-8').decode('unicode_escape')
else:
    root_cert = args.rootcert

"""
Create the spec for input to the API
"""
spec = Tls.Spec(cert=cert,
                key=key,
                root_cert=root_cert)


print('The MACHINE SSL certificate will be replaced with the custom certificate ')
vsphere_client.vcenter.certificate_management.vcenter.Tls.set(spec)
