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
from com.vmware.nsx_policy.model_client import CommunicationMap
from com.vmware.nsx_policy.model_client import CommunicationEntry
from com.vmware.nsx_policy.infra.domains.communication_maps_client import CommunicationEntries
from vmware.vapi.bindings.struct import PrettyPrinter as NsxPrettyPrinter
from com.vmware.nsx_policy.model_client import ApiError

# format NSXT objects for readability
nsx_pp = NsxPrettyPrinter()


class NSXPolicyDFWFirewall(object):
    """
    e.g. Demonstrate access to NSX Policy Manager
    and show access to DFW firewall CRUD operations
    """

    def __init__(self):
        args = parser.parse_args()

        self.nsx_client = create_nsx_policy_client_for_vmc(
            refresh_token=args.refresh_token,
            org_id=args.org_id,
            sddc_id=args.sddc_id)

    def get_group(self, group_id):
        print(' Get Group '.center(70, '='))
        self.cgw_group = self.nsx_client.infra.domains.Groups.get('cgw', group_id)
        nsx_pp.pprint(self.cgw_group)
        return self.cgw_group

    def patch_group(self, group_id, ip_address):
        print(' Create Group '.center(70, '='))
        try:
            ip_address_expression_obj = IPAddressExpression(ip_addresses=[ip_address])  # IP Address of a VM
            group_obj = Group(display_name=group_id, expression=[ip_address_expression_obj])
            self.nsx_client.infra.domains.Groups.patch('cgw', group_id, group_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_group(self, group_id):
        print(' Delete Group '.center(70, '='))
        try:
            self.nsx_client.infra.domains.Groups.delete('cgw', group_id)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def get_communication_map(self):
        print(' Communication Map '.center(70, '='))
        self.communication_map = self.nsx_client.infra.domains.CommunicationMaps.get('cgw', 'application-1')
        nsx_pp.pprint(self.communication_map)
        return self.communication_map

    def patch_communication_map(self):
        print(' Create Communication Map '.center(70, '='))
        try:
            communication_map_obj = CommunicationMap(category='Application', display_name='application-1')
            self.nsx_client.infra.domains.CommunicationMaps.patch('cgw', 'application-1', communication_map_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_communication_map(self):
        print(' Delete Communication Map '.center(70, '='))
        try:
            self.nsx_client.infra.domains.CommunicationMaps.delete('cgw', 'application-1')
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def get_dfw_firewall_rules(self):
        print(' DFW Firewall Rules '.center(70, '='))
        self.dfw_rules = self.nsx_client.infra.domains.communication_maps.CommunicationEntries.get('cgw',
                                                                                                   'application-1', 'AllowPingFromVM1ToVM2')
        nsx_pp.pprint(self.dfw_rules)
        return self.dfw_rules

    def patch_dfw_firewall_rule(self):
        print(' Create DFW Firewall Rule '.center(70, '='))
        self.patch_group('VM1_Group', '172.16.1.2')
        cgw_group1 = self.get_group('VM1_Group')
        self.patch_group('VM2_Group', '172.16.2.2')
        cgw_group2 = self.get_group('VM2_Group')
        try:
            ce_obj = CommunicationEntry(action='ALLOW',
                                        scope=['ANY'],
                                        services=['/infra/services/ICMP-ALL'],
                                        source_groups=[cgw_group1.path],
                                        destination_groups=[cgw_group2.path],
                                        display_name='AllowPingFromVM1ToVM2', sequence_number=10)

            self.nsx_client.infra.domains.communication_maps.CommunicationEntries.patch('cgw', 'application-1',
                                                                                        'AllowPingFromVM1ToVM2', ce_obj)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_dfw_firewall_rule(self):
        print(' Delete DFW Firewall Rule '.center(70, '='))
        try:
            self.nsx_client.infra.domains.communication_maps.CommunicationEntries.delete('cgw', 'application-1',
                                                                                         'AllowPingFromVM1ToVM2')
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
        self.patch_communication_map()
        self.get_communication_map()
        self.patch_dfw_firewall_rule()
        self.get_dfw_firewall_rules()

    def cleanup(self):
        self.delete_dfw_firewall_rule()
        self.delete_communication_map()
        self.delete_group('VM1_Group')
        self.delete_group('VM2_Group')


def main():
    nsx = NSXPolicyDFWFirewall()
    nsx.run()
    nsx.cleanup()


if __name__ == '__main__':
    main()
