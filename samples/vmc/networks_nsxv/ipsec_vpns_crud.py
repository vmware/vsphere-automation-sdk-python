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
from com.vmware.vmc.model_client import Ipsec, IpsecSite, IpsecSites, Subnets
from vmware.vapi.vmc.client import create_vmc_client


class IpsecVPNsCrud(object):
    """
    Demonstrates IPsec VPN CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument(
            '--use-compute-gateway',
            action='store_true',
            default=False,
            help='Use compute gateway. Default is using '
            'management gateway')

        optional_args.add_argument(
            '--vpn-name',
            default='Sample IPsec VPN',
            help='Name of the new VPN')

        optional_args.add_argument(
            '--public-ip',
            default='10.10.10.10',
            help='IP (IPv4) address or FQDN of the Peer')

        optional_args.add_argument(
            '--private-ip',
            default='192.168.10.10',
            help='Local IP of the IPsec Site')

        optional_args.add_argument(
            '--remote-networks',
            default='192.168.20.10/24',
            help='Peer subnets for which VPN is configured')

        optional_args.add_argument(
            '--local-networks',
            default='192.168.30.10/24',
            help='Local subnets for which VPN is configured')

        optional_args.add_argument(
            '--key',
            default='00000000',
            help='Pre Shared Key for the IPsec Site')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')
        args = parser.parse_args()

        self.edge_id = None
        self.site_id = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.vpn_name = args.vpn_name
        self.public_ip = args.public_ip
        self.private_ip = args.private_ip
        self.remote_networks = args.remote_networks
        self.local_networks = args.local_networks
        self.compute_gw = args.use_compute_gateway
        self.key = args.key
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

        print('\n# Setup: List network gateway edges:')
        edges = self.vmc_client.orgs.sddcs.networks.Edges.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_type='gatewayServices').edge_page.data

        print('  Management Gateway ID: {}'.format(edges[0].id))
        print('  Compute Gateway ID: {}'.format(edges[1].id))
        self.edge_id = edges[1].id if self.compute_gw else edges[0].id

    def create_vpn(self):
        if self.compute_gw:
            print('\n# Example: Add a VPN to the Compute Gateway')
        else:
            print('\n# Example: Add a VPN to the Management Gateway')

        ipsec_site = IpsecSite(
            name=self.vpn_name,
            psk=self.key,
            enable_pfs=True,
            authentication_mode='psk',
            peer_subnets=Subnets(subnets=[self.remote_networks]),
            peer_ip=self.public_ip,
            local_ip=self.private_ip,
            encryption_algorithm='aes256',
            enabled=True,
            local_subnets=Subnets(subnets=[self.local_networks]))

        ipsec = Ipsec(enabled=True, sites=IpsecSites(sites=[ipsec_site]))

        # TODO: Find out how to add ipsec networks.
        self.vmc_client.orgs.sddcs.networks.edges.ipsec.Config.update(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            ipsec=ipsec)

        print('# New ipsec_vpn "{}" is added'.format(self.vpn_name))

    def get_vpn(self):
        print('\n# Example: List basic ipsec_vpn specs')
        site = self.get_vpn_by_name(self.vpn_name)
        self.site_id = site.site_id
        self.print_output(site)

    def update_vpn(self):
        print('\n# Example: Update the IPsec VPN')
        updated_name = 'Updated ' + self.vpn_name

        ipsec = self.vmc_client.orgs.sddcs.networks.edges.ipsec.Config.get(
            org=self.org_id, sddc=self.sddc_id, edge_id=self.edge_id)

        for site in ipsec.sites.sites:
            if site.name == self.vpn_name:
                site.name = updated_name

        self.vmc_client.orgs.sddcs.networks.edges.ipsec.Config.update(
            org=self.org_id,
            sddc=self.sddc_id,
            edge_id=self.edge_id,
            ipsec=ipsec)

        print('# List updated VPN specs')
        updated_vpn = self.get_vpn_by_name(updated_name)
        self.print_output(updated_vpn)

    def delete_vpn(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.networks.edges.ipsec.Config.delete(
                org=self.org_id, sddc=self.sddc_id, edge_id=self.edge_id)
            print('\n# Example: IPsec VPN {} is deleted'.format(self.vpn_name))

    def get_vpn_by_name(self, name):
        sites = self.vmc_client.orgs.sddcs.networks.edges.ipsec.Config.get(
            org=self.org_id, sddc=self.sddc_id,
            edge_id=self.edge_id).sites.sites

        for site in sites:
            if site.name == name:
                return site
        else:
            raise Exception("Can't find IPsec VPN with name {}".format(
                self.vpn_name))

    def print_output(self, site):
        print(
            'Name: {}, ID: {}, Public IPs: {}, Private IP: {}, Remote Networks: {}, Local Gateway IP: {}, Local Network {}'
            .format(site.name, site.site_id, site.peer_ip, site.peer_id,
                    site.peer_subnets, site.local_ip, site.local_subnets))


def main():
    ipsec_vpns = IpsecVPNsCrud()
    ipsec_vpns.setup()

    # TODO: Find out which API should be used to add IPsec VPN
    # ipsec_vpns.create_vpn()
    ipsec_vpns.get_vpn()
    ipsec_vpns.update_vpn()
    ipsec_vpns.delete_vpn()


if __name__ == '__main__':
    main()
