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
import base64
import requests
from com.vmware.vcenter.tokenservice_client import TokenExchange
from lxml import etree
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.oauth import create_oauth_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.ssl_helper import get_unverified_session

'''
This sample demonstrates obtaining saml token from access(subject) and id(actor) tokens
The SAML token is then used to connect to VCenter and list all the VM Details

Pre-requisites:
- a VCenter
- access/subject token
- id/actor token

To run the sample,
$ python exchange_access_id_token_for_saml_token.py --vc <VC> --subject_token <Subject Token> --actor_token <Actor Token> --skipverification
'''

HTTP_ENDPOINT = "https://{}/api"
UTF8 = 'utf-8'

parser = argparse.ArgumentParser(description='arguments for obtaining SAML token from access(subject) and id(actor) tokens')

parser.add_argument('--vc', dest='vcenter_server',
                help='VCenter hostname or IP')
parser.add_argument('--subject_token', dest='subject_token',
                help='Subject/Access token')
parser.add_argument('--actor_token', dest='actor_token',
                help='Actor/ID token')
parser.add_argument('--skipverification',
                action='store_true',
                help='Skip Server Certificate Verification')

args = parser.parse_args()

session = requests.session()
if args.skipverification:
    session = get_unverified_session()

stub_config = StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session,
                    url=HTTP_ENDPOINT.format(args.vcenter_server)
                )
            )

# create oauth security context for authentication
oauth_security_context = create_oauth_security_context(args.subject_token)
stub_config.connector.set_security_context(oauth_security_context)

token_exchange = TokenExchange(stub_config)
exchange_spec = token_exchange.ExchangeSpec(
    grant_type=token_exchange.TOKEN_EXCHANGE_GRANT,
    subject_token_type=token_exchange.ACCESS_TOKEN_TYPE,
    actor_token_type=token_exchange.ID_TOKEN_TYPE,
    requested_token_type=token_exchange.SAML2_TOKEN_TYPE,
    actor_token=args.actor_token, subject_token=args.subject_token)
response = token_exchange.exchange(exchange_spec)
saml_token = response.access_token

# convert saml token to saml assertion
samlAssertion = etree.tostring(
    etree.XML(base64.decodebytes(
        bytes(saml_token, UTF8)
    ))
).decode(UTF8)

# create vsphere client to connect to VC and list VM Details
client = create_vsphere_client(server=args.vcenter_server, bearer_token=samlAssertion, session=session)
vms = client.vcenter.VM.list()

print("VM List\n", "-" * 50)
for vm in vms:
    print(vm.name)
print("-" * 50)
