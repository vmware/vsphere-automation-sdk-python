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
Description: Demonstrates the renewal of the MACHINE SSL certificate

Sample Prerequisites:
- The user invoking the API should have the CertificateManagement.Administer privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--duration',
                    help='Duration of time specified in number of days for which the '
                         'MACHINE SSL certificate has to be renewed')

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

if args.duration is None:
    print('Renewing the MACHINE SSL certificate for the duration of ' + str(730) + ' days')
    duration = args.duration
else:
    print('Renewing the MACHINE SSL certificate for the specified duration of ' + args.duration + ' days')
    duration = int(args.duration)

vsphere_client.vcenter.certificate_management.vcenter.Tls.renew(duration)
