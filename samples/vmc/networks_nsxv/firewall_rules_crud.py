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
from com.vmware.vmc.model_client import (AddressFWSourceDestination,
                                         Application, FirewallRules,
                                         Nsxfirewallrule, Nsxfirewallservice)
from vmware.vapi.vmc.client import create_vmc_client


class FirewallRulesCrud(object):
    """
    Demonstrates firewall rule CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument(
            '--rule-name',
            default='Sample Firewall Rule',
            help='Name of the new firewall rule')

        optional_args.add_argument(
            '--use-compute-gateway',
            action='store_true',
            default=False,
            help='Use compute gateway. Default is using '
            'management gateway')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')
        args = parser.parse_args()

        self.edge_id = None
        self.rule_id = None
        self.nfwr = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.rule_name = args.rule_name
        self.compute_gw = args.use_compute_gateway
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

    def create_firewall_rule(self):

        if self.compute_gw:
            print('\n# Example: Add a firewall rule to the Compute Gateway')
        else:
            print('\n# Example: Add a firewall rule to the Management Gateway')

        print('# List network gateway edges:')
        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data

        print('  Management Gateway ID: {}'.format(edges[0].id))
        print('  Compute Gateway ID: {}'.format(edges[1].id))
        self.edge_id = edges[1].id if self.compute_gw else edges[0].id

        sddc = self.vmc_client.orgs.Sddcs.get(self.org_id, self.sddc_id)

        # Construct an destination object for the new firewall rule
        # You can use one of following destination IP addresses
        # IPs for vCenter
        ip_address = [
            sddc.resource_config.vc_public_ip,
            sddc.resource_config.vc_management_ip
        ]

        # TODO: IPs for ESXi
        # TODO: IPs for Site Recovery Manager
        # TODO: IPs for vSphere Replication
        # TODO: IPs for Management Gateway
        # IPs for NSX Manager
        # ip_address = [sddc.resource_config.nsx_mgr_management_ip]

        destination = AddressFWSourceDestination(
            exclude=False,
            ip_address=ip_address,
            grouping_object_id=[],
            vnic_group_id=[])

        # Construct a new NSX firewall rule object
        self.nfwr = Nsxfirewallrule(
            rule_type='user',
            name=self.rule_name,
            enabled=True,
            action='accept',
            source=AddressFWSourceDestination(
                exclude=False,
                ip_address=['any'],
                grouping_object_id=[],
                vnic_group_id=[]),
            destination=destination,
            logging_enabled=False,
            application=Application(
                application_id=[],
                service=[
                    Nsxfirewallservice(
                        source_port=['any'],
                        protocol='TCP',
                        port=['443'],
                        icmp_type=None)
                ]))

        self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.add(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            firewall_rules=FirewallRules([self.nfwr]))

        print('# New firewall rule "{}" is added'.format(self.rule_name))

    def get_firewall_rule(self):

        print('\n# Example: List basic firewall rule specs')
        fw_config = self.vmc_client.orgs.sddcs.networks.edges.firewall.Config.get(
            org=self.org_id, sddc=self.sddc_id, edge_id=self.edge_id)

        fw_rules = fw_config.firewall_rules.firewall_rules

        for r in fw_rules:
            if r.name == self.rule_name:
                self.rule_id = r.rule_id
                break
        else:
            raise Exception("Can't find firewall rule with name {}".format(
                self.rule_name))

        rule = self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            rule_id=self.rule_id)

        self.print_output(rule)

    def update_firewall_rule(self):

        print('\n# Example: Update the firewall rule')
        self.nfwr.description = 'Updated description'
        self.nfwr.name = 'Updated ' + self.rule_name
        self.nfwr.action = 'deny'
        self.nfwr.source.ip_address = ['127.0.0.1']

        self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.update(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            rule_id=self.rule_id,
            nsxfirewallrule=self.nfwr)

        rule = self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            rule_id=self.rule_id)

        print('# List the updated firewall rule specs')
        self.print_output(rule)

    def delete_firewall_rule(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.delete(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id,
                rule_id=self.rule_id)
            print('\n# Example: Firewall rule {} is deleted'.format(
                self.rule_name))

    def print_output(self, rule):
        print(
            'Name: {}, Action: {}, Source IPs: {}, Destination IPs: {},Service Protocol: {}, Service Port: {}'
            .format(rule.name, rule.action, rule.source.ip_address,
                    rule.destination.ip_address,
                    rule.application.service[0].protocol,
                    rule.application.service[0].port))


def main():
    firewall_rules = FirewallRulesCrud()
    firewall_rules.setup()
    firewall_rules.create_firewall_rule()
    firewall_rules.get_firewall_rule()
    firewall_rules.update_firewall_rule()
    firewall_rules.delete_firewall_rule()


if __name__ == '__main__':
    main()
