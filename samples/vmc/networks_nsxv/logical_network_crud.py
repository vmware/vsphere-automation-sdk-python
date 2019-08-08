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
from com.vmware.vmc.model_client import (L2Extension, SddcNetwork,
                                         SddcNetworkAddressGroups,
                                         SddcNetworkAddressGroup,
                                         SddcNetworkDhcpConfig,
                                         SddcNetworkDhcpIpPool)
from vmware.vapi.vmc.client import create_vmc_client


class LogicalNetworkCrud(object):
    """
    Demonstrates logical network CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument(
            '--network-name',
            default='Sample Logical Network',
            help='Name of the new logical network')

        optional_args.add_argument(
            '--subnet',
            default='192.168.100.1/24',
            help='Logical network subnet')

        optional_args.add_argument(
            '--dhcp-range',
            default='192.168.100.2-192.168.100.254',
            help='DHCP IP range for the logical network')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')
        args = parser.parse_args()

        self.network_id = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.network_name = args.network_name
        self.primary_address, self.prefix_length = args.subnet.split('/')
        self.dhcp_range = args.dhcp_range
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

        # Delete logical networks with same name
        networks = self.vmc_client.orgs.sddcs.networks.Logical.get_0(
            org=self.org_id, sddc=self.sddc_id).data
        for network in networks:
            if network.name == self.network_name:
                self.vmc_client.orgs.sddcs.networks.Logical.delete(
                    org=self.org_id, sddc=self.sddc_id, network_id=network.id)
                print('\n# Setup: Logical network "{}" '
                      'with the same name is deleted'.format(network.id))

    def create_logical_network(self):
        print('\n# Example: Add a logical network to the compute gateway')
        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data
        print('  Compute Gateway ID: {}'.format(edges[1].id))
        edge_id = edges[1].id

        # Construct a new NSX logical network spec
        network = SddcNetwork(
            subnets=SddcNetworkAddressGroups(address_groups=[
                SddcNetworkAddressGroup(
                    prefix_length=self.prefix_length,
                    primary_address=self.primary_address)
            ]),
            name=self.network_name,
            cgw_id=edge_id,
            dhcp_configs=SddcNetworkDhcpConfig(ip_pools=[
                SddcNetworkDhcpIpPool(
                    ip_range=self.dhcp_range, domain_name=None)
            ]))

        self.vmc_client.orgs.sddcs.networks.Logical.create(
            org=self.org_id, sddc=self.sddc_id, sddc_network=network)

        print('\n# New logical network "{}" is added'.format(
            self.network_name))

    def get_logical_network(self):
        print('\n# Example: List all logical networks')
        networks = self.vmc_client.orgs.sddcs.networks.Logical.get_0(
            org=self.org_id, sddc=self.sddc_id).data

        self.print_output(networks)

        for network in networks:
            if network.name == self.network_name:
                self.network_id = network.id
                break
        else:
            raise Exception("Can't find logical network with name {}".format(
                self.network_name))

        print('\n# Get the new logical network specs')
        network = self.vmc_client.orgs.sddcs.networks.Logical.get(
            org=self.org_id, sddc=self.sddc_id, network_id=self.network_id)

        self.print_output([network])

    def update_logical_network(self):
        print('\n# Example: Update the logical network')
        network = self.vmc_client.orgs.sddcs.networks.Logical.get(
            org=self.org_id, sddc=self.sddc_id, network_id=self.network_id)
        network.l2_extension = L2Extension(123)
        network.subnets = None
        network.dhcp_configs = None

        self.vmc_client.orgs.sddcs.networks.Logical.update(
            org=self.org_id,
            sddc=self.sddc_id,
            network_id=self.network_id,
            sddc_network=network)

        network = self.vmc_client.orgs.sddcs.networks.Logical.get(
            org=self.org_id, sddc=self.sddc_id, network_id=self.network_id)

        print('# List the updated logical network specs')
        self.print_output([network])

    def delete_logical_network(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.networks.Logical.delete(
                org=self.org_id, sddc=self.sddc_id, network_id=self.network_id)
            print('\n# Example: Logical network "{}" is deleted'.format(
                self.network_name))

    def print_output(self, networks):
        for network in networks:
            print('Gateway: {}, Network ID: {}, Network Name: {}, Subnets: {}'.
                  format(
                      network.cgw_name, network.id, network.name,
                      '{}/{}'.format(
                          network.subnets.address_groups[0].primary_address,
                          network.subnets.address_groups[0].prefix_length)))


def main():
    logical_network_crud = LogicalNetworkCrud()
    logical_network_crud.setup()
    logical_network_crud.create_logical_network()
    logical_network_crud.get_logical_network()
    # TODO: figure out the requirements for updating logical network
    # logical_network_crud.update_logical_network()
    logical_network_crud.delete_logical_network()


if __name__ == '__main__':
    main()
