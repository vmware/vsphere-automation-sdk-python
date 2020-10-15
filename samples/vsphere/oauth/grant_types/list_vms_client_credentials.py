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
    import login_using_client_credentials
import argparse

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2020 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0+'

"""
To run this sample,
$ python list_vms_client_credentials.py --server <VC_IP> \
    -- client_id <client_id> --client_secret <client_secret> --skipverification
"""

parser = argparse.ArgumentParser()
parser.add_argument("--server",
                    help="VC IP or hostname")
parser.add_argument("--client_id",
                    help="Client/Application ID of the server to server app")
parser.add_argument("--client_secret",
                    help="Client/Application secret \
                        of the server to server app")
parser.add_argument('--skipverification',
                    action='store_true',
                    help='Verify server certificate when connecting to vc.')

args = parser.parse_args()

session = get_unverified_session() if args.skipverification else None
saml_assertion = login_using_client_credentials(
                    args.server,
                    session,
                    args.client_id,
                    args.client_secret)

client = create_vsphere_client(
            server=args.server,
            bearer_token=saml_assertion,
            session=session)
vms = client.vcenter.VM.list()
print(vms)
