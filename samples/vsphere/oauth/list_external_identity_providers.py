"""
* *******************************************************
* Copyright VMware, Inc. 2019. All Rights Reserved.
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
__vcenter_version__ = '6.8.7+'

import argparse
import requests
from com.vmware.vcenter.identity_client import Providers
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from samples.vsphere.common.ssl_helper import get_unverified_session
from vmware.vapi.lib.connect import get_requests_connector

'''
This sample lists all the external Identity Providers for the given VCenter

Pre-requisites:
- a VCenter

To run the sample,
$ python list_external_identity_providers.py --vc <VC> --skipverification
'''

HTTP_ENDPOINT = "https://{}/api"

parser = argparse.ArgumentParser(description='arguments for listing external Identity Providers')

parser.add_argument('--vc', dest='vcenter_server',
                help='VCenter hostname or IP')
parser.add_argument('--skipverification',
                action='store_true',
                help='Skip Server Certificate Verification')

args = parser.parse_args()

session = requests.session()
if args.skipverification:
    session = get_unverified_session()

stub_config = StubConfigurationFactory.new_std_configuration(get_requests_connector(session=session, url=HTTP_ENDPOINT.format(args.vcenter_server)))

# use the identity client to list the providers
id_client = Providers(stub_config)
providers = id_client.list()
print("Total providers: {}\n".format(len(providers)))
print("-" * 100)

# print summary of the providers
for p in providers:
    print("Auth Endpoint: {}\n".format(p.oauth2.auth_endpoint))
    print("Token Endpoint: {}\n".format(p.oauth2.token_endpoint))
    print("-" * 100)
