#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
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
from samples.vsan.snapservice.data_protection_clients import DataProtectionClients


class PGSnapshots(object):

    def __init__(self, snapservice_client, cluster_mo_id, pg_id):
        self._snapservice_client = snapservice_client
        self._cluster_mo_id = cluster_mo_id
        self._pg_id = pg_id

    def list(self):
        return self._snapservice_client.clusters.protection_groups.Snapshots.list(self._cluster_mo_id, self._pg_id)

    def get(self, snapshot_id):
        return self._snapservice_client.clusters.protection_groups.Snapshots.get(self._cluster_mo_id, self._pg_id,
                                                                                 snapshot_id)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--cluster_mo_id',
                               action='store',
                               required=True,
                               help='Cluster MoRef ID where the snapshots locate')
    required_args.add_argument('--pg_id',
                               action='store',
                               required=True,
                               help='Protection group ID where the snapshots locate')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)
    snapshot_id = None

    pg_snapshots = PGSnapshots(clients.snapservice_client, args.cluster_mo_id, args.pg_id)

    print("List of protection group's snapshots:")
    print("----------------------------------------")
    pg_snapshots_list = pg_snapshots.list()
    for snapshot in pg_snapshots_list.snapshots:
        print(snapshot)
        print("----------------------------------------")
        snapshot_id = snapshot.snapshot

    if snapshot_id is not None:
        print('\nGet protection group snapshot for id: {}'.format(snapshot_id))
        print("----------------------------------------")
        snapshot = pg_snapshots.get(snapshot_id)
        print(snapshot)


if __name__ == '__main__':
    main()
