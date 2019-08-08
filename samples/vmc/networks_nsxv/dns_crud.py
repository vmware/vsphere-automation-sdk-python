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
from com.vmware.vmc.model_client import DnsForwarders
from vmware.vapi.vmc.client import create_vmc_client


class DNSCrud(object):
    """
    Demonstrates DNS CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument('--use-compute-gateway',
                            action='store_true',
                            default=False,
                            help='Use compute gateway. Default is using '
                                 'management gateway')

        optional_args.add_argument('--cleardata',
                            action='store_true',
                            help='Clean up after sample run')
        args = parser.parse_args()

        self.edge_id = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.compute_gw = args.use_compute_gateway
        self.cleanup = args.cleardata
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

        print('\n# Setup: List network gateway edges:')
        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data

        print('  Management Gateway ID: {}'.format(edges[0].id))
        print('  Compute Gateway ID: {}'.format(edges[1].id))

        if self.compute_gw:
            self.edge_id = edges[1].id
            print('# Use Compute Gateway in this Sample')
        else:
            self.edge_id = edges[0].id
            print('# Use Management Gateway in this Sample')

    def get_dns(self):
        print('\n# Example: List basic DNS specs')

        # Get the first DNS
        dns = self.vmc_client.orgs.sddcs.networks.edges.dns.Config.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id).dns_views.dns_view[0]

        self.print_output(dns)

    def enable_disable_dns(self):
        if self.compute_gw:
            print('\n# Example: Enable or disable Compute Gateway DNS')
        else:
            print('\n# Example: Enable or disable DNS Management Gateway DNS')

        dns_config = self.vmc_client.orgs.sddcs.networks.edges.dns.Config.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id)

        new_state = True
        if dns_config.enabled:
            print('# DNS was enabled. Disable it now..')
            new_state = False
        else:
            print('# DNS was disabled. Enable it now..')

        self.vmc_client.orgs.sddcs.networks.edges.dns.Config.create(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            enable=new_state)

    def update_dns(self):
        print('\n# Example: Update the DNS IP Addresses')

        dns_config = self.vmc_client.orgs.sddcs.networks.edges.dns.Config.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id)

        dns_config.dns_views.dns_view[0].forwarders = DnsForwarders(
            ip_address=['9.9.9.9', '9.9.4.4'])

        self.vmc_client.orgs.sddcs.networks.edges.dns.Config.update(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            dns_config=dns_config
        )

        print('# List updated DNS specs')
        updated_vpn = self.vmc_client.orgs.sddcs.networks.edges.dns.Config.get(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id).dns_views.dns_view[0]
        self.print_output(updated_vpn)

    def delete_dns(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.networks.edges.dns.Config.delete(
                org=self.org_id,
                sddc=self.sddc_id,
                edge_id=self.edge_id)
            print('\n# Example: DNS is deleted')

    def print_output(self, dns):
        # DNS IP address might be empty
        ips = getattr(dns.forwarders, 'ip_address', [])
        print('Name: {}, IP Addresses: {}'.format(dns.name, ips))


def main():
    dns_crud = DNSCrud()
    dns_crud.setup()
    dns_crud.get_dns()
    dns_crud.enable_disable_dns()
    dns_crud.update_dns()
    dns_crud.delete_dns()


if __name__ == '__main__':
    main()
