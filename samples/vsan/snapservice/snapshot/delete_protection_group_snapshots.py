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


class DeleteProtectionGroupSnapshots(object):
    """
    Description: Demonstrates deleting protection group snapshots.

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
        required_args.add_argument('--pgname',
                                   action='store',
                                   required=True,
                                   help='Protection group to delete snapshot')

        parser.add_argument_group('snapservice optional arguments')\
              .add_argument('--remain',
                            action='store',
                            help='How many protection group snapshots to leave')

        args = sample_util.process_cli_args(parser.parse_args())
        self.cluster = args.cluster
        self.pgname = args.pgname
        self.remain = int(args.remain) if int(args.remain) > 0 else 0

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

        # Get protection group identifier
        pgs_info = self.ssClient.snapservice.clusters.ProtectionGroups.list(clusterId)
        pgId = 0
        for pg_info in pgs_info.items:
            if pg_info.info.name == self.pgname:
                pgId = pg_info.pg
        print("\nProtection groups '{}': '{}'\n".format(self.pgname, pgId))

        # Get protection group snapshots
        snapshots_info = self.ssClient.snapservice.clusters.protection_groups\
            .Snapshots.list(clusterId, pgId)
        print("\n\nGet snapshots:\n{}".format(snapshots_info))

        # Get snapshot to delete
        snapshotTimeMap = {}
        for snapshot in snapshots_info.snapshots:
            snapshotTimeMap[snapshot.info.expires_at] = snapshot.snapshot

        timeToDel = []
        if self.remain == 0:
            timeToDel = sorted(snapshotTimeMap)
        elif self.remain < len(snapshotTimeMap):
            timeToDel = sorted(snapshotTimeMap)[0:-self.remain]
        else:
            print("\n\n No snapshot to delete.\n")

        for time in timeToDel:
            print("\n\n##Deleting pg snapshot '{}' which will expire at '{}'"
                  .format(snapshotTimeMap[time], time))
            task = self.ssClient.snapservice.clusters.protection_groups\
                .Snapshots.delete(clusterId, pgId, snapshotTimeMap[time])


def main():
    delete_pg_snapshot = DeleteProtectionGroupSnapshots()
    delete_pg_snapshot.run()


if __name__ == '__main__':
    main()
