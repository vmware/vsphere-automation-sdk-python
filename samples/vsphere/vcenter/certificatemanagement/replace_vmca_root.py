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
from com.vmware.vcenter.certificate_management.vcenter_client import VmcaRoot
from samples.vsphere.common import (sample_cli, sample_util)

"""
Description: Demonstrates the replacement of the VMCA ROOT certificate and
regeneration of all the other certificates on vCenter.

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Administer privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--keysize',
                    help='Key size used to generate the private key.'
                         'keysize will take 2048 bits if not provided')

parser.add_argument('--commonname',
                    help='Common name of the certificate subject field.'
                         'Defaults to PNID (Primary Network Identifier).')

parser.add_argument('--organization',
                    help='Organization field in certificate subject.')

parser.add_argument('--organizationunit',
                    help='Organization unit field in certificate subject')

parser.add_argument('--locality',
                    help='Locality field in the certificate subject')

parser.add_argument('--stateorprovince',
                    help='State field in certificate subject')

parser.add_argument('--country',
                    help='Country field in the certificate subject')

parser.add_argument('--emailaddress',
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
    key_size = args.keysize
else:
    key_size = int(args.keysize)
if args.subjectaltname is None:
    subject_alt_name = args.subjectaltname
else:
    subject_alt_name = args.subjectaltname.split(',')

"""
Create the spec for input to the API
"""
spec = VmcaRoot.CreateSpec(key_size=key_size,
                           common_name=common_name,
                           organization=organization,
                           organization_unit=organization_unit,
                           locality=locality,
                           state_or_province=state_or_province,
                           country=country,
                           email_address=email_address,
                           subject_alt_name=subject_alt_name)

print('Replacing the VMCA ROOT certificate and regenerating all other certificates')
vsphere_client.vcenter.certificate_management.vcenter.VmcaRoot.create(spec)
