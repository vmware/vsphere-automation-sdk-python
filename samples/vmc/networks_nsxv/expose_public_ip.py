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
__vcenter_version__ = 'VMware Cloud on AWS'

import random

from samples.vmc.helpers.sample_cli import parser, required_args, optional_args
from com.vmware.vmc.model_client import *
from vmware.vapi.vmc.client import create_vmc_client
from samples.vmc.helpers.vmc_task_helper import wait_for_task


class ExposePublicIP(object):
    """
    Demo steps required to expose a VM to public internet
        1. Request a public IP address
        2. Add a firewall rule on compute gateway to access to the VM
        3. Create a NAT rule to forward traffic from public IP to private IP

    Sample Prerequisites:
        - A VM deployed inside the SDDC with private IP address
    """

    def __init__(self):
        optional_args.add_argument('--notes',
                            default='Sample public IP ' + str(random.randint(0, 100)),
                            help='Notes of the new public IP')

        optional_args.add_argument('--fw-rule-name',
                            default='Sample firewall rule ' + str(random.randint(0, 100)),
                            help='Name of the compute gae')

        optional_args.add_argument('--nat-rule-description',
                            default='Sample NAT rule ' + str(random.randint(0, 100)),
                            help='Description for the NAT rule')

        required_args.add_argument('--internal-ip',
                            required=True,
                            help='Private IP of the VM')

        optional_args.add_argument('--cleardata',
                            action='store_true',
                            help='Clean up after sample run')
        args = parser.parse_args()

        self.network_id = None
        self.edge_id = None
        self.nat_rule_id = None
        self.public_ip = None
        self.nfwr = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.notes = args.notes
        self.fw_rule_name = args.fw_rule_name
        self.nat_rule_description = args.nat_rule_description
        self.internal_ip = args.internal_ip
        self.cleardata = args.cleardata
        self.vmc_client = create_vmc_client(args.refresh_token)

    def setup(self):
        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".
                             format(self.sddc_id, self.org_id))

        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data
        print('\n# Setup: Compute Gateway ID: {}'.format(edges[1].id))
        self.edge_id = edges[1].id

    def request_public_ip(self):
        print('\n# Example: Request a new IP for SDDC')
        ip_spec = SddcAllocatePublicIpSpec(names=[self.notes], count=1)
        task = self.vmc_client.orgs.sddcs.Publicips.create(
            org=self.org_id,
            sddc=self.sddc_id,
            spec=ip_spec)

        wait_for_task(task_client=self.vmc_client.orgs.Tasks,
                      org_id=self.org_id,
                      task_id=task.id,
                      interval_sec=2)

        ips = self.vmc_client.orgs.sddcs.Publicips.list(
            org=self.org_id,
            sddc=self.sddc_id)

        for ip in ips:
            if ip.name == self.notes:
                self.ip_id = ip.allocation_id
                self.public_ip = ip.public_ip
                print('# Successfully requested public IP {}'.
                      format(ip.public_ip))
                break
        else:
            raise Exception("Can't find public IP with notes {}".
                            format(self.notes))

    def create_firewall_rule_on_cgw(self):

        print('\n# Example: Add a firewall rule to the compute gateway')

        # Construct a new NSX firewall rule object
        # which allow any to any traffic
        self.nfwr = Nsxfirewallrule(rule_type='user',
                                    name=self.fw_rule_name,
                                    enabled=True,
                                    action='accept',
                                    source=AddressFWSourceDestination(
                                        exclude=False,
                                        ip_address=['any'],
                                        grouping_object_id=[],
                                        vnic_group_id=[]),
                                    destination=AddressFWSourceDestination(
                                        exclude=False,
                                        ip_address=['any'],
                                        grouping_object_id=[],
                                        vnic_group_id=[]),
                                    logging_enabled=False,
                                    application=None)

        self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.add(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            firewall_rules=FirewallRules([self.nfwr]))

        print(' # New firewall rule "{}" is added'.format(self.fw_rule_name))

    def create_net_rule(self):

        print('\n# Example: Add a NAT rule to the compute gateway')

        # Construct a new NSX NAT rule spec
        rule = Nsxnatrule(vnic='0',
                          rule_type='user',
                          action='dnat',  # Supported types are DNAT|SNAT
                          protocol='any',
                          description=self.nat_rule_description,
                          original_address=self.public_ip,
                          original_port='any',
                          translated_address=self.internal_ip,
                          translated_port='any',
                          enabled=True)

        self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.add(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            nat_rules=NatRules([rule]))

        print(' # New NAT rule "{}" is added'.format(self.nat_rule_description))

    def cleanup(self):
        if self.cleardata:

            # Delete the firewall rule
            fw_rules = self.vmc_client.orgs.sddcs.networks.edges.firewall.Config.get(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id).firewall_rules.firewall_rules

            for r in fw_rules:
                if r.name == self.fw_rule_name:
                    self.vmc_client.orgs.sddcs.networks.edges.firewall.config.Rules.delete(
                        org=self.org_id,
                        sddc=self.sddc_id,
                        edge_id=self.edge_id,
                        rule_id=r.rule_id)
                break
            print('\n# Cleanup: Firewall rule {} is deleted'.
                  format(self.fw_rule_name))

            # Delete the NAT rule
            rules = self.vmc_client.orgs.sddcs.networks.edges.nat.Config.get(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id).rules.nat_rules_dtos
            for rule in rules:
                if rule.description == self.nat_rule_description:
                    self.vmc_client.orgs.sddcs.networks.edges.nat.config.Rules.delete(
                        org=self.org_id,
                        sddc=self.sddc_id,
                        edge_id=self.edge_id,
                        rule_id=rule.rule_id)
            print('\n# Cleanup: NAT rule "{}" is deleted'.
                  format(self.nat_rule_description))

            # Release the public IP address
            self.vmc_client.orgs.sddcs.Publicips.delete(
                org=self.org_id,
                sddc=self.sddc_id,
                id=self.ip_id)
            print('\n# Cleanup: Public IP "{}" is released'.
                  format(self.public_ip))


def main():
    expose_public_ip = ExposePublicIP()
    expose_public_ip.setup()
    expose_public_ip.request_public_ip()
    expose_public_ip.create_firewall_rule_on_cgw()
    expose_public_ip.create_net_rule()
    expose_public_ip.cleanup()


if __name__ == '__main__':
    main()
