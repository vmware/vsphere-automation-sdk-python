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
from samples.vsphere.vcenter.setup import testbed
from samples.vsan.snapservice.vsan_snapservice_client import create_snapservice_client

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter_client import (Cluster, VM)
from com.vmware.snapservice_client import *
from com.vmware.snapservice.clusters_client import *
from com.vmware.snapservice.tasks_client import Status


class CreateProtectionGroup(object):
    """
    Description: Demonstrates creating protection group.

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
        self.cleardata = args.cleardata

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
        self.clusterId = clusterId
        print("\nGot cluster '{}' id: {}".format(self.cluster, clusterId))

        # Get vm identifier
        vm_names = set(testbed.config["VM_NAMES"].split(","))
        vm_list = self.vcClient.vcenter.VM.list(VM.FilterSpec(names=vm_names))

        vm_ids = []
        for vm_info in vm_list:
            vm_ids.append(vm_info.vm)
        print("\nGot VM list: {}".format(vm_ids))

        # Get vm formats
        vm_formats = testbed.config["VM_FORMATS"].split(",")

        # Build protection group Spec
        target_entities = TargetEntities(vm_name_patterns=vm_formats, vms=set(vm_ids))
        snapshot_policies = [SnapshotPolicy(name='policy1',
                                   schedule=SnapshotSchedule(
                                       TimeUnit(testbed.config["SCHEDULE_UNIT"]),
                                                testbed.config["SCHEDULE"]),
                                   retention=RetentionPeriod(
                                       TimeUnit(testbed.config["RETENTION_UNIT"]),
                                                testbed.config["RETENTION"]))]
        locked = testbed.config["LOCK"]

        spec = ProtectionGroupSpec(name=testbed.config["PG_NAME"],
                           target_entities=target_entities,
                           snapshot_policies=snapshot_policies,
                           locked=locked)
        print("\n###Creating protection group with spec:\n")
        print(spec)

        # Wait for task to complete.
        task = self.ssClient.snapservice.clusters.ProtectionGroups.create_task(clusterId, spec=spec)

        while True:
            task_info = self.ssClient.snapservice.Tasks.get(task.get_task_id())

            if task_info.status == Status.SUCCEEDED:
                print("\n###Creation task {} succeeds.".format(task_info.description.id))
                return
            elif task_info.status == Status.FAILED:
                print("\n###Creation task {} fails.\nError:\n".format(task_info.description.id))
                print(task_info.error)
                return
            else:
                print("\n###Creation task {} progress: {}".format(task_info.description.id,
                                                                  task_info.progress.completed))
                time.sleep(5)

    def cleanup(self):
        pgs_info = self.ssClient.snapservice.clusters.ProtectionGroups.list(self.clusterId)

        for pg_info in pgs_info.items:
            if pg_info.info.name == testbed.config["PG_NAME"] and not testbed.config["LOCK"]:
                print("\n###Deleting created PG {}".format(testbed.config["PG_NAME"]))
                self.ssClient.snapservice.clusters.ProtectionGroups.delete_task(
                        self.clusterId, pg_info.pg, ProtectionGroups.DeleteSpec(force=True))


def main():
    create_pg = CreateProtectionGroup()
    create_pg.run()
    if create_pg.cleardata:
        create_pg.cleanup()


if __name__ == '__main__':
    main()
