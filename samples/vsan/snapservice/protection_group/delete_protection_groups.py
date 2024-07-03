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

import time

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsan.snapservice.vsan_snapservice_client import create_snapservice_client

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter_client import Cluster
from com.vmware.snapservice_client import *
from com.vmware.snapservice.clusters_client import *
from com.vmware.snapservice.tasks_client import Status


class DeleteProtectionGroups(object):
    """
    Description: Demonstrates deleting protection groups.

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
        required_args.add_argument('--pgnames',
                                   action='store',
                                   required=True,
                                   help='Protection groups to delete, separate with comma.')

        parser.add_argument_group('snapservice optional arguments')\
              .add_argument('--force',
                            action='store_true',
                            help='Whether delete protection group snapshots')

        args = sample_util.process_cli_args(parser.parse_args())
        self.cluster = args.cluster
        self.pgnames = args.pgnames
        self.force = True if args.force else False

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

        pg_names = self.pgnames.split(",")
        pgs_info = self.ssClient.snapservice.clusters.ProtectionGroups.list(clusterId)
        tasks = []
        for pg_info in pgs_info.items:
            if pg_info.info.name in pg_names:
                if pg_info.info.locked:
                    print("\nProtection group '{}' is mutabl, skip the deletion."
                          .format(pg_info.info.name))

                elif pg_info.info.status == ProtectionGroupStatus.MARKED_FOR_DELETE:
                    print("\nProtection group '{}' is marked as deleted, skip the "
                          "deletion.".format(pg_info.info.name))

                else:
                    print("\nDeleting protection group '{}' : '{}'"
                          .format(pg_info.info.name, pg_info.pg))

                    task = self.ssClient.snapservice.clusters.ProtectionGroups.delete_task(
                        clusterId, pg_info.pg, ProtectionGroups.DeleteSpec(force=self.force))
                    print("Task id: {}\n".format(task.get_task_id()))
                    tasks.append(task.get_task_id())

        taskCompleted = 0
        while True:

            for taskId in tasks:
                task_info = self.ssClient.snapservice.Tasks.get(taskId)

                if task_info.status == Status.SUCCEEDED:
                    print("\n###Deletion task {} succeeds.".format(task_info.description.id))
                    taskCompleted += 1
                elif task_info.status == Status.FAILED:
                    print("\n###Deletion task {} fails.\nError:\n".format(task_info.description.id))
                    print(task_info.getResult())
                    taskCompleted += 1
                else:
                    print("\n###Deletion task {} progress: ".format(task_info.description.progress))

            if taskCompleted >= len(tasks):
                print("\n\n###All protection group deletion jobs are completed")
                break

            time.sleep(5)


def main():
    delete_pg = DeleteProtectionGroups()
    delete_pg.run()


if __name__ == '__main__':
    main()
