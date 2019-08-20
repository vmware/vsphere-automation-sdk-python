#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2018. All Rights Reserved.
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

from samples.vmc.helpers.sample_cli import parser, optional_args
from com.vmware.vmc.model_client import Nsxnatrule, NatRules
from vmware.vapi.vmc.client import create_vmc_client


class NatRuleCrud(object):
    """
    Demonstrates NAT rule CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument(
            '--public-ip', help='Public IP range for the NAT rule')

        optional_args.add_argument(
            '--rule-description',
            default='Sample NAT rule',
            help='Description for the rule')

        optional_args.add_argument(
            '--internal-ip',
            default='192.168.200.1/24',
            help='NAT rule subnet')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')
        args = parser.parse_args()

        self.network_id = None
        self.edge_id = None
        self.rule_id = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.public_ip = args.public_ip
        self.internal_ip = args.internal_ip
        self.rule_description = args.rule_description
        self.internal_ip = args.internal_ip
        self.cleanup = args.cleardata
        self.vmc_client = create_vmc_client(args.refresh_token)

    def setup(self):
        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(
                self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".format(
                self.sddc_id, self.org_id))

        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data
        print('\n# Setup: Compute Gateway ID: {}'.format(edges[1].id))
        self.edge_id = edges[1].id

        # Delete NAT rules with same name
        rules = self.get_nat_rules_by_description(self.rule_description)
        for rule in rules:
            self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.delete(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id,
                rule_id=rule.rule_id)
            print('\n# Setup: NAT Rule "{}" '
                  'with the same name is deleted'.format(rule.description))

    def create_net_rule(self):
        print('\n# Example: Add a NAT rule to the compute gateway')

        # Construct a new NSX NAT rule spec
        rule = Nsxnatrule(
            vnic='0',
            rule_type='user',
            action='dnat',  # Supported types are DNAT|SNAT
            protocol='tcp',
            description=self.rule_description,
            original_address=self.public_ip,
            original_port='443',
            translated_address=self.internal_ip,
            translated_port='443',
            enabled=True)

        self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.add(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            nat_rules=NatRules([rule]))

        print('\n# New NAT rule "{}" is added'.format(self.rule_description))

    def get_net_rule(self):
        print('\n# Example: List all NAT rules')
        rules = self.vmc_client.orgs.sddcs.networks.edges.nat.Config.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_id=self.edge_id).rules.nat_rules_dtos
        self.print_output(rules)

    def update_net_rule(self):
        print("\n# Example: Update the NAT rule")

        rule = self.get_nat_rules_by_description(self.rule_description)[0]
        rule.Description = 'Updated' + self.rule_description
        rule.original_port = 'any'

        self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.update(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            rule_id=rule.rule_id,
            nsxnatrule=rule)

        self.rule_id = rule.rule_id

        print('# List the updated NAT rule specs')
        rule = self.get_nat_rules_by_description(self.rule_description)[0]
        self.print_output([rule])

    def delete_net_rule(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.delete(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id,
                rule_id=self.rule_id)
            print('\n# Example: NAT rule "{}" is deleted'.format(
                self.rule_description))

    def get_nat_rules_by_description(self, description):
        rules = self.vmc_client.orgs.sddcs.networks.edges.nat.Config.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_id=self.edge_id).rules.nat_rules_dtos
        result = []
        for rule in rules:
            if rule.description == description:
                result.append(rule)
        return result

    def print_output(self, rules):
        for rule in rules:
            print(
                'Description: {}, Rule ID: {}, Action: {}, Public IP: {}, Public Ports: {}, Internal IP: {}, Internal Ports: {}'
                .format(rule.description, rule.rule_id, rule.action,
                        rule.original_address, rule.original_port,
                        rule.translated_address, rule.translated_port))


def main():
    net_rule_crud = NatRuleCrud()
    net_rule_crud.setup()
    net_rule_crud.create_net_rule()
    net_rule_crud.get_net_rule()
    net_rule_crud.update_net_rule()
    net_rule_crud.delete_net_rule()


if __name__ == '__main__':
    main()
