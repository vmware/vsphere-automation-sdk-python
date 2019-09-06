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
from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


"""
Update a NSX-T Group on MGW or CGW

Sample Prerequisites:
    - SDDC deployed in VMware Cloud on AWS
    - A NSX-T security group
"""
optional_args.add_argument('--gateway_type',
                    default='mgw',
                    help='Gateway type. Either mgw or cgw')

optional_args.add_argument('--group_id',
                    help='ID of the group to be updated')

required_args.add_argument('--name',
                    required=True,
                    help='New name of the security group to be updated')

args = parser.parse_args()

gateway_type = args.gateway_type.lower()

nsx_client = create_nsx_policy_client_for_vmc(
        refresh_token=args.refresh_token,
        org_id=args.org_id,
        sddc_id=args.sddc_id)

try:
    security_group = nsx_client.infra.domains.Groups.get(gateway_type, args.group_id)
except NotFound:
    raise ValueError('Security group "{}" not found'.format(args.group_id))

print('Updating NSX-T security group\'s name from "{}" to "{}"\n'.format(
    security_group.display_name, args.name))

new_description = 'new description'
security_group.description = new_description
security_group.display_name = args.name

group_updated = nsx_client.infra.domains.Groups.update(gateway_type, args.group_id, security_group)
assert group_updated.description == new_description
assert group_updated.display_name == args.name
print('Successfully updated the security group\n')
