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
from samples.vsan.snapservice.tasks.task_utils import wait_for_snapservice_task

from com.vmware.snapservice_client import ProtectionGroupUpdateSpec, TargetEntities
from com.vmware.vcenter_client import Cluster


class ProtectionGroups(object):
    def __init__(self, vsphere_client, snapservice_client, cluster_name):
        self._vsphere_client = vsphere_client
        self._snapservice_client = snapservice_client

        # This is to demonstrate how to get cluster ID by cluster name
        cluster_list = self._vsphere_client.vcenter.Cluster.list(
            Cluster.FilterSpec(names={cluster_name}))
        self._cluster_id = cluster_list[0].cluster

    def list(self):
        return self._snapservice_client.clusters.ProtectionGroups.list(self._cluster_id)

    def get(self, pg_id):
        return self._snapservice_client.clusters.ProtectionGroups.get(self._cluster_id, pg_id)

    def update_task(self, pg_id, update_spec):
        return self._snapservice_client.clusters.ProtectionGroups.update_task(self._cluster_id, pg_id, spec=update_spec)

    def pause_task(self, pg_id):
        return self._snapservice_client.clusters.ProtectionGroups.pause_task(self._cluster_id, pg_id)

    def resume_task(self, pg_id):
        return self._snapservice_client.clusters.ProtectionGroups.resume_task(self._cluster_id, pg_id)

    def delete_task(self, pg_id):
        return self._snapservice_client.clusters.ProtectionGroups.delete_task(self._cluster_id, pg_id)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--cluster_name',
                               action='store',
                               required=True,
                               help='Cluster name where the protection group locates')
    required_args.add_argument('--action',
                               action='store',
                               required=True,
                               help='Action to perform on the protection group: list/get/pause/resume/update/delete')
    parser.add_argument('--pg_id',
                        action='store',
                        help='Protection group ID to perform action on')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    pg_id = args.pg_id
    clients = DataProtectionClients(args)
    pgs = ProtectionGroups(clients.vsphere_client, clients.snapservice_client, args.cluster_name)

    if args.action == 'list':
        print("List of protection groups:")
        print("----------------------------------------")
        pgs_list = pgs.list()
        for pg in pgs_list.items:
            print(pg)
            print("----------------------------------------")
    else:
        if pg_id is None:
            print('Please specify the protection group ID to perform action on.')
            return

        if args.action == 'get':
            print('Get protection group for id: {}'.format(pg_id))
            print("----------------------------------------")
            print(pgs.get(pg_id))
        if args.action == 'pause':
            print('----------------------------------------')
            pause_task = pgs.pause_task(pg_id)
            print('Pause protection group task: {}'.format(pause_task.task_id))
            wait_for_snapservice_task(clients.snapservice_client, pause_task.task_id)
            print('Protection group paused task done, its pg status: {}'.format(pgs.get(pg_id).status))
        if args.action == 'resume':
            print('----------------------------------------')
            resume_task = pgs.resume_task(pg_id)
            print('Resume protection group task: {}'.format(resume_task.task_id))
            wait_for_snapservice_task(clients.snapservice_client, resume_task.task_id)
            print('Protection group resumed task done, its pg status: {}'.format(pgs.get(pg_id).status))
        if args.action == 'update':
            print('----------------------------------------')
            # Just update the target VMs to protect only in the protection group
            update_spec = ProtectionGroupUpdateSpec(target_entities=TargetEntities(vms={'vm-42', 'vm-44'}))
            update_task = pgs.update_task(pg_id, update_spec)
            print('Update protection group task: {}'.format(update_task.task_id))
            wait_for_snapservice_task(clients.snapservice_client, update_task.task_id)
            print('Updated protection group: {}'.format(pgs.get(pg_id)))
        if args.action == 'delete':
            print('----------------------------------------')
            delete_task = pgs.delete_task(pg_id)
            print('Delete protection group task: {}'.format(delete_task.task_id))
            wait_for_snapservice_task(clients.snapservice_client, delete_task.task_id)
            print('Protection group delete task done, its pg status: {}'.format(pgs.get(pg_id).status))


if __name__ == '__main__':
    main()
