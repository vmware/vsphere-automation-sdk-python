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
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.oauth.grant_types.oauth_utility \
    import login_using_password
import argparse

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2020 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0+'

"""
To run this sample,
$ python list_vms_password --server <VC_IP> \
    --username <username> --password <password> --skipverification
"""

parser = argparse.ArgumentParser()
parser.add_argument("--server",
                    help="VC IP or hostname")
parser.add_argument("--username",
                    help="username to login \
                        to vCenter")
parser.add_argument("--password",
                    help="password to login \
                        to vCenter")
parser.add_argument('--skipverification',
                    action='store_true',
                    help='Verify server certificate when connecting to vc.')

args = parser.parse_args()

session = get_unverified_session() if args.skipverification else None
saml_assertion = login_using_password(
                    args.server,
                    session,
                    args.username,
                    args.password)

client = create_vsphere_client(
            server=args.server,
            bearer_token=saml_assertion,
            session=session)
vms = client.vcenter.VM.list()
print(vms)
