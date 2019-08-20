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
__vcenter_version__ = '6.8.1+'

import requests

from samples.vmc.helpers.sample_cli import parser
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from com.vmware.nsx_vmc_app_client_for_vmc import create_nsx_vmc_app_client_for_vmc
from com.vmware.nsx_vmc_app.model_client import PublicIp
from com.vmware.nsx_policy.model_client import PolicyNatRule
from vmware.vapi.bindings.struct import PrettyPrinter as NsxPrettyPrinter
from com.vmware.nsx_policy.model_client import ApiError

# format NSXT objects for readability
nsx_pp = NsxPrettyPrinter()


class NSXPolicyNAT(object):
    """
    e.g. Demonstrate access to NSX Policy Manager and
    show access to NAT CRUD operations
    """

    def __init__(self):
        args = parser.parse_args()

        self.nsx_client = create_nsx_policy_client_for_vmc(
            refresh_token=args.refresh_token,
            org_id=args.org_id,
            sddc_id=args.sddc_id)

        self.nsx_vmc_app_client = create_nsx_vmc_app_client_for_vmc(
            refresh_token=args.refresh_token,
            org_id=args.org_id,
            sddc_id=args.sddc_id)

    def get_public_ip(self):
        print(' Public IPs '.center(70, '='))
        self.public_ips = self.nsx_vmc_app_client.infra.PublicIps.get('VM1_IP')
        self.public_ip = self.public_ips.ip
        nsx_pp.pprint(self.public_ip)
        return self.public_ip

    def update_public_ip(self):
        print(' Create Public IP '.center(70, '='))
        try:
            public_ip_obj = PublicIp(display_name='VM1_IP')
            self.nsx_vmc_app_client.infra.PublicIps.update('VM1_IP', public_ip_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_public_ip(self):
        print(' Delete Public IP '.center(70, '='))
        try:
            self.nsx_vmc_app_client.infra.PublicIps.delete('VM1_IP')
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def get_nat_rules(self):
        print(' NAT Rules '.center(70, '='))
        self.nat = self.nsx_client.infra.tier_1s.nat.NatRules.list('cgw', 'USER')
        self.nat_rules = self.nat.results
        nsx_pp.pprint(self.nat_rules)
        return self.nat_rules

    def patch_nat_rule(self):
        print(' Create NAT Rule '.center(70, '='))
        self.update_public_ip()
        public_ip = self.get_public_ip()
        try:
            nat_obj = PolicyNatRule(action='REFLEXIVE',
                                    scope=['/infra/labels/cgw-public'],
                                    source_network='172.16.1.2',
                                    translated_network=public_ip,
                                    display_name='VM1NatRule', sequence_number=1)
            self.nsx_client.infra.tier_1s.nat.NatRules.patch('cgw', 'USER', 'VM1NatRule', nat_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_nat_rule(self):
        print(' Delete NAT Rule '.center(70, '='))
        try:
            self.nsx_client.infra.tier_1s.nat.NatRules.delete('cgw', 'USER', 'VM1NatRule')
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
        self.patch_nat_rule()
        self.get_nat_rules()

    def cleanup(self):
        self.delete_nat_rule()
        self.get_nat_rules()
        self.delete_public_ip()


def main():
    nsx = NSXPolicyNAT()
    nsx.run()
    nsx.cleanup()


if __name__ == '__main__':
    main()
