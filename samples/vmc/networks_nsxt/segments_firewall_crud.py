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

import requests
from samples.vmc.helpers.sample_cli import parser
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from com.vmware.nsx_policy.model_client import Rule
from vmware.vapi.bindings.struct import PrettyPrinter as NsxPrettyPrinter
from com.vmware.nsx_policy.model_client import ApiError

# format NSXT objects for readability
nsx_pp = NsxPrettyPrinter()


class NSXPolicySegmentFirewall(object):
    """
    e.g. Demonstrate access to NSX Policy Manager and show
    access to infra, tier1s, segments and firewall CRUD operations
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

    def get_tier1s(self):
        print(' Tier1s '.center(70, '='))
        self.tier1s = self.nsx_client.infra.Tier1s.list()
        nsx_pp.pprint(self.tier1s)
        return self.tier1s

    def get_segments(self):
        print(' Segments '.center(70, '='))
        self.segments = self.nsx_client.infra.tier_1s.Segments.list('cgw')
        nsx_pp.pprint(self.segments)
        return self.segments

    def get_domains(self):
        print(' Domains '.center(70, '='))
        self.domains = self.nsx_client.infra.Domains.list()
        nsx_pp.pprint(self.domains)
        return self.domains

    def get_mgw_gateway_firewall_rules(self):
        print(' Firewall Rules '.center(70, '='))
        self.mgw_policies = self.nsx_client.infra.domains.GatewayPolicies.get('mgw', 'default')
        self.mgw_rules = self.mgw_policies.rules
        nsx_pp.pprint(self.mgw_rules)
        return self.mgw_rules

    def patch_mgw_gateway_firewall_rule(self):
        print(' Patch Vcenter inbound '.center(70, '='))
        try:
            rule_obj = Rule(action='ALLOW',
                            scope=['/infra/labels/mgw'],
                            services=['/infra/services/HTTPS'],
                            source_groups=['ANY'],
                            destination_groups=['/infra/domains/mgw/groups/VCENTER'],
                            display_name='InboundAccess-vCenter', sequence_number=0)

            self.nsx_client.infra.domains.gateway_policies.Rules.patch('mgw', 'default', 'InboundAccess-vCenter',
                                                                       rule_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_mgw_gateway_firewall_rule(self):
        print(' Deleting Vcenter inbound FW Rule '.center(70, '='))
        try:
            self.nsx_client.infra.domains.gateway_policies.Rules.delete('mgw', 'default', 'InboundAccess-vCenter')
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
        self.get_tier1s()
        self.get_segments()
        self.get_domains()
        self.get_mgw_gateway_firewall_rules()
        self.patch_mgw_gateway_firewall_rule()
        self.get_mgw_gateway_firewall_rules()

    def cleanup(self):
        self.delete_mgw_gateway_firewall_rule()
        self.get_mgw_gateway_firewall_rules()  # check to ensure deletion


def main():
    nsx = NSXPolicySegmentFirewall()
    nsx.run()
    nsx.cleanup()


if __name__ == '__main__':
    main()
