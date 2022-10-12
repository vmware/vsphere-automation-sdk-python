#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2022. All Rights Reserved.
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
__copyright__ = 'Copyright 2022 VMware, Inc. All rights reserved.'
__vcenter_version__ = '8.0.0+'

import typing

from com.vmware.vcenter.namespace_management_client import Supervisors
from com.vmware.vcenter.namespace_management.supervisors_client import ControlPlane, Workloads, SizingHint
from com.vmware.vcenter.namespace_management.networks_client import Network, VSphereNetwork, NetworkType
import com.vmware.vcenter.namespace_management.networks_client as net
import com.vmware.vcenter.namespace_management.networks.service_client as net_svc
from com.vmware.vcenter.namespace_management.networks.edges_client import Edge, HAProxyConfig, EdgeProvider, Server

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration

NTP_SERVERS = ["pool.ntp.org"]


def dns_servers(args) -> typing.Optional[net_svc.DNS]:
    dns_spec = None
    servers = args.split(",")
    if not servers:
        dns_spec = net_svc.DNS(servers=servers, search_domains=[])
    return dns_spec


def create_zones_enable_spec(args) -> Supervisors.EnableOnZonesSpec:
    """
    Creates an enablement spec for WCP across multiple zones using VDS for workload networking.
    """
    control_plane_spec = ControlPlane(
        size=SizingHint.TINY,  # Tests assume this is set to TINY. It is later updated to SMALL.
        login_banner='Welcome to Supervisor on vSphere Zones!',
        storage_policy=args.control_plane_storage_policy,
        floating_ip_address=args.control_plane_floating_ip_address,
        network=Network(
            network=NetworkType.VSPHERE,
            vsphere=VSphereNetwork(
                dvpg=args.control_plane_network_vsphere_dvpg
            ),
            services=net.Services(
                dns=dns_servers(args.control_plane_network_services_dns_servers),
                ntp=net_svc.NTP(servers=NTP_SERVERS)
            ),
        )
    )
    workload_spec = Workloads(
        network=Network(
            network=NetworkType.VSPHERE,
            ip_management=net.IPManagement(
                dhcp_enabled=False,
                gateway_address="192.168.1.1/16",
                ip_assignments=[
                    net.IPAssignment(
                        assignee=net.IPAssignment.Assignment.SERVICE,
                        ranges=[net.IPRange(
                            address="172.24.0.0",
                            count=65536
                        )]
                    ),
                    net.IPAssignment(
                        assignee=net.IPAssignment.Assignment.NODE,
                        ranges=[net.IPRange(
                            address="192.168.128.0",
                            count=256
                        )]
                    )
                ]
            ),
            vsphere=VSphereNetwork(
                dvpg=args.workloads_network_vsphere_dvpg
            ),
            services=net.Services(
                dns=dns_servers(args.workloads_network_services_dns_servers),
                ntp=net_svc.NTP(servers=NTP_SERVERS)
            ),
        ),
        edge=Edge(
            id="lb-1",
            load_balancer_address_ranges=[net.IPRange(
                address="192.168.0.1",
                count=256
            )],
            provider=EdgeProvider.HAPROXY,
            haproxy=HAProxyConfig(
                servers=[Server(
                    host=args.workloads_edge_haproxy_servers,
                    port=5556
                )],
                username=args.workloads_edge_haproxy_username,
                password=args.workloads_edge_haproxy_password,
                certificate_authority_chain=args.workloads_edge_haproxy_certificate_authority_chain,
            )
        )
    )
    return Supervisors.EnableOnZonesSpec(
        name=args.name,
        zones=args.zones,
        control_plane=control_plane_spec,
        workloads=workload_spec
    )


class EnableSupervisorsOnZones(object):
    """
    Demonstrates enabling Supervisors on given zones.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('--name',
                            required=True,
                            help='A user-friendly identifier for this Supervisor.')
        parser.add_argument('--zones',
                            required=True,
                            help='List of consumption fault domain zones available for Supervisors and its workloads.')

        # control plane enable configuration
        parser.add_argument('--control-plane-storage-policy',
                            required=True,
                            help='Identifies the storage policy backing the Supervisor Kubernetes API server.')
        parser.add_argument('--control-plane-floating-ip-address',
                            required=True,
                            help='Floating IP address for supervisors')
        parser.add_argument('--control-plane-network-vsphere-dvpg',
                            required=True,
                            help='The Managed Object ID of a vSphere Distributed Virtual Port Group for Control Plane.')
        parser.add_argument('--control-plane-network-services-dns-servers',
                            required=True,
                            help='List of control plane DNS servers')

        # workloads enable configuration
        parser.add_argument('--workloads-network-vsphere-dvpg',
                            required=True,
                            help='The Managed Object ID of a vSphere Distributed Virtual Switch for workloads.')
        parser.add_argument('--workloads-network-services-dns-servers',
                            required=True,
                            help='List of workloads DNS servers.')

        # load balancer enable configuration
        parser.add_argument('--workloads-edge-haproxy-servers',
                            required=True,
                            help='List of the addresses for the data plane API servers used to configure Virtual '
                                 'Servers.')
        parser.add_argument('--workloads-edge-haproxy-username',
                            required=True,
                            help='Used by the HAProxy Kubernetes Operator to program the HAProxy Controller.')
        parser.add_argument('--workloads-edge-haproxy-password',
                            required=True,
                            help='Used for securing HAProxy username.')
        parser.add_argument('--workloads-edge-haproxy-certificate-authority-chain',
                            required=True,
                            help='PEM-encoded CA chain which is used to verify x509 certificates received from the '
                                 'server.')

        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
            args.server, args.username, args.password,
            session)
        self.supervisor_enable_on_zones = Supervisors(stub_config)
        self.spec = create_zones_enable_spec(args)

    def run(self):
        supervisor_id = self.supervisor_enable_on_zones.enable_on_zones(self.spec)
        print('supervisor_id: {0}'.format(supervisor_id))


def main():
    list_cl = EnableSupervisorsOnZones()
    list_cl.run()


if __name__ == '__main__':
    main()
