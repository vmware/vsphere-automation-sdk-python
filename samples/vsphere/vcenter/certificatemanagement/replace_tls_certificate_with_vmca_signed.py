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
Description: Demonstrates the replacement of the MACHINE SSL certificate with a
VMCA signed certificate.

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Administer privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--keysize',
                    help='Key size used to generate the key pair.'
                         'keysize will take 2048 bits if not modified')

parser.add_argument('--commonname',
                    help='Common name of the certificate subject field.'
                         'Common name will take Primary Network Identifier(PNID) if not modified.')

parser.add_argument('--organization',
                    required=True,
                    help='Organization field in certificate subject.')

parser.add_argument('--organizationunit',
                    required=True,
                    help='Organization unit field in certificate subject')

parser.add_argument('--locality',
                    required=True,
                    help='Locality field in the certificate subject')

parser.add_argument('--stateorprovince',
                    required=True,
                    help='State field in certificate subject')

parser.add_argument('--country',
                    required=True,
                    help='Country field in the certificate subject')

parser.add_argument('--emailaddress',
                    required=True,
                    help='Email field in Certificate extensions')

parser.add_argument('--subjectaltname',
                    help='subjectaltname is list of Dns Names and Ip addresses')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

common_name = args.commonname
organization = args.organization
organization_unit = args.organizationunit
locality = args.locality
state_or_province = args.stateorprovince
country = args.country
email_address = args.emailaddress

if args.keysize is None:
    keysize = args.keysize
else:
    keysize = int(args.keysize)

if args.subjectaltname is None:
    subjectaltname = args.subjectaltname
else:
    subjectaltname = args.subjectaltname.split(',')

"""
Create the spec for input to the API
"""
spec = Tls.ReplaceSpec(key_size=keysize,
                       common_name=common_name,
                       organization=organization,
                       organization_unit=organization_unit,
                       locality=locality,
                       state_or_province=state_or_province,
                       country=country,
                       email_address=email_address,
                       subject_alt_name=subjectaltname)


print('Replacing the MACHINE SSL certificate with a new VMCA generated certificate')
vsphere_client.vcenter.certificate_management.vcenter.Tls.replace_vmca_signed(spec)
