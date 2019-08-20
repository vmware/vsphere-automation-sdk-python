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

import random

import requests

from samples.vmc.helpers.sample_cli import parser, required_args, optional_args
from com.vmware.nsx_policy.infra_client import Domains
from com.vmware.nsx_policy.model_client import (Expression, Group,
                                                IPAddressExpression)
from com.vmware.nsx_policy_client_for_vmc import \
    create_nsx_policy_client_for_vmc
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
"""
Create a new NSX-T Group on MGW or CGW

Sample Prerequisites:
    - SDDC deployed in VMware Cloud on AWS
"""
optional_args.add_argument('--gateway_type',
                    default='mgw',
                    help='Gateway type. Either mgw or cgw')

required_args.add_argument('--name',
                    required=True,
                    help='Name of the security group to be created')

optional_args.add_argument('--ip_address',
                    default='172.31.0.0/24',
                    help='IP address for the expression')

optional_args.add_argument('--group_id',
                    help='ID of the group. A random ID will be used by default')

args = parser.parse_args()

gateway_type = args.gateway_type.lower()

id = args.group_id or 'AppGroup-{}'.format(random.randint(1, 10))

nsx_client = create_nsx_policy_client_for_vmc(
    refresh_token=args.refresh_token, org_id=args.org_id, sddc_id=args.sddc_id)

print('Create a new NSX-T security group for "{}" with id "{}" and name "{}" \n'
      .format(gateway_type, id, args.name))

ipa = IPAddressExpression(ip_addresses=[args.ip_address])
group = Group(display_name=args.name, expression=[ipa])

nsx_client.infra.domains.Groups.update(gateway_type, id, group)

print('Successfully created the security group\n')

print('Retrieve security group properties\n')
security_group = nsx_client.infra.domains.Groups.get(gateway_type, id)
print(security_group)
