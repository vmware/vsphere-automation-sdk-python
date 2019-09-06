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

from samples.vmc.helpers.sample_cli import parser, required_args
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from vmware.vapi.bindings.struct import PrettyPrinter as NsxPrettyPrinter
from com.vmware.nsx_policy.model_client import ApiError
from com.vmware.nsx_policy.model_client import L3VpnSubnet
from com.vmware.nsx_policy.model_client import RouteBasedL3VpnSession
from com.vmware.nsx_policy.model_client import PolicyBasedL3VpnSession
from com.vmware.nsx_policy.model_client import L3VpnSession
from com.vmware.nsx_policy.model_client import L3VpnRule
from com.vmware.nsx_policy.model_client import BgpNeighborConfig
from com.vmware.nsx_policy.model_client import TunnelSubnet
from com.vmware.nsx_policy.model_client import L3Vpn

# format NSXT objects for readability
nsx_pp = NsxPrettyPrinter()


class NSXPolicyL3VPN(object):
    """
    e.g. Demonstrate access to NSX Policy Manager and show
    L3VPN CRUD operations
    """

    def __init__(self):
        required_args.add_argument('--remote_endpoint_public_ip',
                            required=True,
                            help='L3 VPN Remote end point\'s public ip')

        required_args.add_argument('--passphrase',
                            required=True,
                            help='Passphrase used for VPN')

        self.args = parser.parse_args()

        self.nsx_client = create_nsx_policy_client_for_vmc(
            refresh_token=self.args.refresh_token,
            org_id=self.args.org_id,
            sddc_id=self.args.sddc_id)

    def get_l3_vpn_context(self):
        print(' Get L3VPN Context '.center(70, '='))
        try:
            context = self.nsx_client.infra.tier_0s.locale_services.L3vpnContext.get("vmc", "default")
            nsx_pp.pprint(context)
            return context
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def create_policy_based_l3_vpn(self, vpn_id):
        print(' Create policy based L3VPN '.center(70, '='))
        try:
            context = self.get_l3_vpn_context()
            local_end_point_ip = context.available_local_addresses[0].address_value
            print("local_end_point_ip={}".format(local_end_point_ip))
            destination_subnet = [L3VpnSubnet(subnet="10.3.0.0/16")]  # Value should be per the user setup config
            source_subnet = [L3VpnSubnet(subnet="10.2.0.0/16")]  # Value should be per the user setup config

            self.l3vpn_rule = L3VpnRule(
                revision=0,
                description="rule 1",
                display_name="rule1",
                resource_type=L3VpnSession.RESOURCE_TYPE_POLICYBASEDL3VPNSESSION,
                action=L3VpnRule.ACTION_PROTECT,
                destinations=destination_subnet,
                sequence_number=0,
                id="rule-" + vpn_id,
                sources=source_subnet)
            l3vpn_session = PolicyBasedL3VpnSession(resource_type=L3VpnSession.RESOURCE_TYPE_POLICYBASEDL3VPNSESSION,
                                                    rules=[self.l3vpn_rule])

            self.l3VPN = L3Vpn(
                revision=0,
                id=vpn_id,
                description="Example policy based L3VPN",
                display_name="Example policy based L3VPN",
                resource_type=L3VpnSession.RESOURCE_TYPE_POLICYBASEDL3VPNSESSION,
                dh_groups=[L3Vpn.DH_GROUPS_GROUP14],
                enable_perfect_forward_secrecy=True,
                enabled=True,
                ike_digest_algorithms=[L3Vpn.IKE_DIGEST_ALGORITHMS_SHA1],  # Value should be per the user setup config
                ike_encryption_algorithms=[L3Vpn.IKE_ENCRYPTION_ALGORITHMS_128],
                # Value should be per the user setup config
                ike_version=L3Vpn.IKE_VERSION_V1,  # Value should be per the user setup config
                l3vpn_session=l3vpn_session,
                local_address=local_end_point_ip,
                passphrases=[self.args.passphrase],
                remote_public_address=self.args.remote_endpoint_public_ip,
                tunnel_digest_algorithms=[L3Vpn.TUNNEL_DIGEST_ALGORITHMS_SHA1],
                # Value should be per the user setup config
                tunnel_encryption_algorithms=[L3Vpn.TUNNEL_ENCRYPTION_ALGORITHMS_128]
                # Value should be per the user setup config
            )
            self.nsx_client.infra.tier_0s.locale_services.L3vpns.patch("vmc", "default",
                                                                       l3vpn_id=vpn_id, l3_vpn=self.l3VPN)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def create_route_based_l3_vpn(self, vpn_id):
        print(' Create route based L3VPN '.center(70, '='))
        try:
            context = self.get_l3_vpn_context()
            local_end_point_ip = context.available_local_addresses[0].address_value
            print("local_end_point_ip={}".format(local_end_point_ip))
            tunnel_subnet = TunnelSubnet(ip_addresses=["169.254.2.1"],  # Value should be per the user setup config
                                         prefix_length=24)  # Value should be per the user setup config
            bgpconfig1 = BgpNeighborConfig(links=None,
                                           description="bgp neighbor config",
                                           display_name="bgp_neighbor_config_1",
                                           id="bgp_neighbor_config_1",
                                           neighbor_address="169.254.2.2",  # Value should be per the user setup config
                                           remote_as_num=str(65002))  # Value should be per the user setup config
            self.nsx_client.infra.tier_0s.locale_services.bgp.Neighbors.patch(tier0_id="vmc",
                                                                              locale_service_id="default",
                                                                              neighbor_id="rb_neighbor_1",
                                                                              bgp_neighbor_config=bgpconfig1)

            neighbor_list = self.nsx_client.infra.tier_0s.locale_services.bgp.Neighbors.list(tier0_id="vmc",
                                                                                             locale_service_id="default"
                                                                                             )
            print("List of neighbors={}".format(neighbor_list))
            get_neighbhor = self.nsx_client.infra.tier_0s.locale_services.bgp.Neighbors.get(
                tier0_id="vmc", locale_service_id="default", neighbor_id="rb_neighbor_1")
            print("get_neighbhor={}".format(get_neighbhor))

            l3vpn_session = RouteBasedL3VpnSession(routing_config_path=get_neighbhor.path,
                                                   tunnel_subnets=[
                                                       tunnel_subnet],
                                                   resource_type=L3VpnSession.RESOURCE_TYPE_ROUTEBASEDL3VPNSESSION)
            self.l3VPN = L3Vpn(
                revision=0,
                id=vpn_id,
                description="vpn config from automation",
                display_name="Example route based L3VPN",
                resource_type=L3VpnSession.RESOURCE_TYPE_ROUTEBASEDL3VPNSESSION,
                dh_groups=[L3Vpn.DH_GROUPS_GROUP14],
                enable_perfect_forward_secrecy=True,
                enabled=True,  # To enabel/disable the VPN
                ike_digest_algorithms=[L3Vpn.IKE_DIGEST_ALGORITHMS_SHA1],  # Value should be per the user setup config
                ike_encryption_algorithms=[L3Vpn.IKE_ENCRYPTION_ALGORITHMS_128],
                # Value should be per the user setup config
                ike_version=L3Vpn.IKE_VERSION_V1,  # Value should be per the user setup config
                l3vpn_session=l3vpn_session,
                local_address=local_end_point_ip,
                passphrases=[self.args.passphrase],
                remote_public_address=self.args.remote_endpoint_public_ip,
                tunnel_digest_algorithms=[L3Vpn.TUNNEL_DIGEST_ALGORITHMS_SHA1],
                # Value should be per the user setup config
                tunnel_encryption_algorithms=[L3Vpn.TUNNEL_ENCRYPTION_ALGORITHMS_128]
                # Value should be per the user setup config
            )
            self.nsx_client.infra.tier_0s.locale_services.L3vpns.patch("vmc", "default",
                                                                       l3vpn_id=vpn_id, l3_vpn=self.l3VPN)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def list_l3_vpns(self):
        print(' List L3VPN '.center(70, '='))
        try:
            list_of_vpns = self.nsx_client.infra.tier_0s.locale_services.L3vpns.list("vmc", "default")
            for vpn_entry in list_of_vpns.results:
                nsx_pp.pprint(vpn_entry)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def get_l3_vpn(self, vpn_id):
        print(' Get L3VPN '.center(70, '='))
        try:
            vpn_entry = self.nsx_client.infra.tier_0s.locale_services.L3vpns.get("vmc", "default", vpn_id)
            nsx_pp.pprint(vpn_entry)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_l3vpn(self, vpn_id):
        print(' Delete L3VPN '.center(70, '='))
        try:
            self.nsx_client.infra.tier_0s.locale_services.L3vpns.delete("vmc", "default", vpn_id)
        except Exception as ex:
            print(ex)
            self.log_error(ex)

    def delete_bgp_neighbor(self, neighbor_id):
        print(' Delete BGP Neighbor '.center(70, '='))
        try:
            self.nsx_client.infra.tier_0s.locale_services.bgp.Neighbors.delete(tier0_id="vmc",
                                                                               locale_service_id="default",
                                                                               neighbor_id=neighbor_id)
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

    def run_policy_based_vpn(self):
        self.create_policy_based_l3_vpn(vpn_id="example_policy_vpn_1")
        self.list_l3_vpns()
        self.get_l3_vpn(vpn_id="example_policy_vpn_1")

    def cleanup_policy_based_vpn(self):
        self.delete_l3vpn(vpn_id="example_policy_vpn_1")

    def run_route_based_vpn(self):
        self.create_route_based_l3_vpn(vpn_id="example_route_vpn_1")
        self.list_l3_vpns()
        self.get_l3_vpn(vpn_id="example_route_vpn_1")

    def cleanup_route_based_vpn(self):
        self.delete_bgp_neighbor(neighbor_id="rb_neighbor_1")
        self.delete_l3vpn(vpn_id="example_route_vpn_1")


def main():
    nsx = NSXPolicyL3VPN()
    nsx.run_policy_based_vpn()
    nsx.cleanup_policy_based_vpn()
    nsx.run_route_based_vpn()
    nsx.cleanup_route_based_vpn()


if __name__ == '__main__':
    main()
