#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2024 Broadcom. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0.3+'

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsan.snapservice.vsan_snapservice_client import create_snapservice_client

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter_client import Cluster
from com.vmware.snapservice_client import *
from com.vmware.snapservice.clusters_client import *


class ListProtectionGroups(object):
    """
    Description: Demonstrates listing protection groups.

    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()

        required_args = parser.add_argument_group(
            'snapservice required arguments')
        required_args.add_argument('--snapservice',
                                   action='store',
                                   required=True,
                                   help='Snapservice IP/hostname to connect to')
        required_args.add_argument('--cluster',
                                   action='store',
                                   required=True,
                                   help='Cluster where the protection group locates')

        args = sample_util.process_cli_args(parser.parse_args())
        self.cluster = args.cluster

        skipverification = True if args.skipverification else False
        vcSession = get_unverified_session() if skipverification else None
        self.vcClient = create_vsphere_client(server=args.server,
                                              username=args.username,
                                              password=args.password,
                                              session=vcSession)

        ssSession = get_unverified_session() if skipverification else None
        self.ssClient = create_snapservice_client(server=args.snapservice,
                                                  vc=args.server,
                                                  username=args.username,
                                                  password=args.password,
                                                  session=ssSession,
                                                  skip_verification=skipverification)

    def run(self):
        # Get cluster identifier
        cluster_spec = set([self.cluster])
        cluster_list = self.vcClient.vcenter.Cluster.list(
            Cluster.FilterSpec(names=cluster_spec))

        clusterId = cluster_list[0].cluster
        print("\nGot cluster '{}' id: {}".format(self.cluster, clusterId))

        pgs_info = self.ssClient.snapservice.clusters.ProtectionGroups.list(clusterId)
        print("\n\nList of protection groups:\n")
        for pg_info in pgs_info.items:
            print(pg_info)
            print("----------------------------------------\n")


def main():
    list_pg = ListProtectionGroups()
    list_pg.run()


if __name__ == '__main__':
    main()
