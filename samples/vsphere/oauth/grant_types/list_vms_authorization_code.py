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

from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.oauth.grant_types.oauth_utility \
    import login_using_authorization_code

from urllib.parse import parse_qs
import webbrowser
import urllib.parse as urlparse
import requests
import uuid
import argparse

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2020 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0+'

"""
To run this sample,

In a different tab, keep the webserver running,
$ python webserver.py

Then execute the following
$ python list_vms_authorization_code.py --server <VC_IP> \
    --client_id <client_id> --client_secret <client_secret> \
    --org_id <org_id> --skipverification
"""

parser = argparse.ArgumentParser()
parser.add_argument("--server",
                    help="VC IP or hostname")
parser.add_argument("--client_id",
                    help="Client/Application ID of the webapp")
parser.add_argument("--client_secret",
                    help="Client/Application secret \
                        of the webapp")
parser.add_argument("--redirect_uri",
                    help="Redirect uri \
                        given at the time of client registration")
parser.add_argument('--skipverification',
                    action='store_true',
                    help='Verify server certificate when connecting to vc.')

args = parser.parse_args()


def get_auth_code_and_state(url):
    openbrowser(url)
    parsed = urlparse.urlparse(url)
    redirect_uri = parse_qs(parsed.query)['redirect_uri']

    get_code_uri = redirect_uri[0].rsplit('/', 1)[0]
    get_code_uri = get_code_uri + "/getcode"

    response = get_response(get_code_uri)
    while "code" not in response or response == '':
        response = get_response(get_code_uri)

    res = response.split(':')
    code = res[1]
    state = res[3]
    return [code, state]


def openbrowser(url):
    webbrowser.open(url)
    pass


def get_response(url):
    response = requests.get(url)
    return response.text


session = get_unverified_session() if args.skipverification else None
saml_assertion = login_using_authorization_code(
                    args.server,
                    session,
                    args.client_id,
                    args.client_secret,
                    args.redirect_uri,
                    get_auth_code_and_state)
client = create_vsphere_client(
            server=args.server,
            bearer_token=saml_assertion,
            session=session)
vms = client.vcenter.VM.list()
print(vms)
