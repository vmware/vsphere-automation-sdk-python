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

__author__ = 'VMware, Inc.'
__vcenter_version__ = '6.8.0+'

import requests
from samples.vmc.helpers.sample_cli import parser
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from com.vmware.nsx_policy.model_client import IPAddressExpression
from com.vmware.nsx_policy.model_client import Group
from com.vmware.nsx_policy.model_client import Rule
from vmware.vapi.bindings.struct import PrettyPrinter as NsxPrettyPrinter
from com.vmware.nsx_policy.model_client import ApiError

# format NSXT objects for readability
nsx_pp = NsxPrettyPrinter()


class NSXPolicyCGWFirewall(object):
    """
    e.g. Demonstrate access to NSX Policy Manager and
    show access to infra and CGW firewall CRUD operations
    """

    def __init__(self):
        args = parser.parse_args()

        self.nsx_client = create_nsx_policy_client_for_vmc(
            refresh_token=args.refresh_token,
            org_id=args.org_id,
            sddc_id=args.sddc_id)

    def get_infra(self):
        print(' Infra '.center(70, '='))
        self.infra = self.nsx_client.Infra.get()
        nsx_pp.pprint(self.infra)
        return self.infra

    def get_domains(self):
        print(' Domains '.center(70, '='))
        self.domains = self.nsx_client.infra.Domains.list()
        nsx_pp.pprint(self.domains)
        return self.domains

    def get_group(self):
        print(' Get Group '.center(70, '='))
        self.cgw_group = self.nsx_client.infra.domains.Groups.get('cgw', 'VM1_Group')
        nsx_pp.pprint(self.cgw_group)
        return self.cgw_group

    def patch_group(self):
        print(' Create Group '.center(70, '='))
        try:
            ip_address_expression_obj = IPAddressExpression(ip_addresses=['172.16.1.2'])  # IP Address of a VM
            group_obj = Group(display_name='VM1_Group', expression=[ip_address_expression_obj])
            self.nsx_client.infra.domains.Groups.patch('cgw', 'VM1_Group', group_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_group(self):
        print(' Delete Group '.center(70, '='))
        try:
            self.nsx_client.infra.domains.Groups.delete('cgw', 'VM1_Group')
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def get_cgw_gateway_firewall_rules(self):
        print(' CGW Firewall Rules '.center(70, '='))
        self.cgw_policies = self.nsx_client.infra.domains.GatewayPolicies.get('cgw', 'default')
        self.cgw_rules = self.cgw_policies.rules
        nsx_pp.pprint(self.cgw_rules)
        return self.cgw_rules

    def patch_cgw_gateway_firewall_rule(self):
        print(' Create CGW Firewall Rule '.center(70, '='))
        self.patch_group()
        cgw_group = self.get_group()
        try:
            rule_obj = Rule(action='ALLOW',
                            scope=['/infra/labels/cgw-all'],
                            services=['/infra/services/ICMP-ALL'],
                            source_groups=['ANY'],
                            destination_groups=[cgw_group.path],
                            display_name='AllowPingToVM1', sequence_number=0)

            self.nsx_client.infra.domains.gateway_policies.Rules.patch('cgw', 'default', 'AllowPingToVM1',
                                                                       rule_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_cgw_gateway_firewall_rule(self):
        print(' Delete CGW Firewall Rule '.center(70, '='))
        try:
            self.nsx_client.infra.domains.gateway_policies.Rules.delete('cgw', 'default', 'AllowPingToVM1')
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def log_error(self, ex):
        """
        Generic error logger that will use NSXT API Error message decoders for
        more descriptive information on errors
        """
        api_error = ex.data.convert_to(ApiError)
        print("Error configuring {}".format(api_error.error_message))
        print("{}".format(api_error.__dict__))
        print("{}".format(api_error.details))

    def run(self):
        self.get_infra()
        self.get_domains()
        self.get_cgw_gateway_firewall_rules()
        self.patch_cgw_gateway_firewall_rule()
        self.get_cgw_gateway_firewall_rules()

    def cleanup(self):
        self.delete_cgw_gateway_firewall_rule()
        self.get_cgw_gateway_firewall_rules()
        self.delete_group()


def main():
    nsx = NSXPolicyCGWFirewall()
    nsx.run()
    nsx.cleanup()


if __name__ == '__main__':
    main()
