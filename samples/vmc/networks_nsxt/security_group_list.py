#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc'
__vcenter_version__ = 'VMware Cloud on AWS'

import requests

from samples.vmc.helpers.sample_cli import parser, optional_args
from com.vmware.nsx_policy.infra_client import Domains
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


"""
List all Network Security Groups

Sample Prerequisites:
    - SDDC deployed in VMware Cloud on AWS
"""
optional_args.add_argument('--gateway_type',
                    default='mgw',
                    help='Gateway type. Either mgw or cgw')

args = parser.parse_args()

gateway_type = args.gateway_type.lower()

nsx_client = create_nsx_policy_client_for_vmc(
        refresh_token=args.refresh_token,
        org_id=args.org_id,
        sddc_id=args.sddc_id)

print('Listing all security groups for "{}"\n'.format(gateway_type))

security_groups = nsx_client.infra.domains.Groups.list(gateway_type).results

for group in security_groups:
    print('* Group "{}":'.format(group.id))
    print('{}\n'.format(group))
