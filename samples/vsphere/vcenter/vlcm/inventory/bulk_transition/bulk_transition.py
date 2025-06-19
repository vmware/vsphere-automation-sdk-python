#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
* and/or its subsidiaries.
* SPDX-License-Identifier: MIT
* *******************************************************
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '9.0.0+'

import time

from com.vmware.esx.settings_client import Inventory
from com.vmware.esx.settings.inventory.reports.transition_summary_client import Hosts
from com.vmware.esx.settings.inventory.reports.transition_summary_client import Clusters
from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.vcenter.hcl.utils import get_configuration

SUCCEEDED_KEY = "SUCCEEDED"
FAILED_KEY = "FAILED"
BLOCKED_KEY = "BLOCKED"

# With a 1 second sleep this is equal to roughly 5 minutes
TIME_OUT_ITERATIONS = 300


class BulkTransitionSvc:
    """
    Demonstrates triggering the "transition" workflow for a group of clusters or standalone hosts
    for the bulk transition feature, waiting for the task to complete, and getting the result.

    Prerequisites:
        - A datacenter
        - If a cluster is used as an entity, cluster should have at least one host.
        - Host with version >= 7.0.2
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument("--entityType",
                            required=True,
                            help="Type of entity")
        parser.add_argument("--entities",
                            action="extend", nargs="+", type=str,
                            required=True,
                            help="MoID of the target clusters/hosts")
        args = sample_util.process_cli_args(parser.parse_args())
        self.entityType = args.entityType
        self.entities = set(args.entities)
        self.config = get_configuration(args.server, args.username,
                                   args.password,
                                   args.skipverification)

    def run(self):
        entity_spec = None
        if (self.entityType.casefold() == "cluster".casefold()):
            entity_spec = Inventory.EntitySpec(type=Inventory.EntitySpec.InventoryType.CLUSTER, clusters=self.entities)
        elif (self.entityType.casefold() == "host".casefold()):
            entity_spec = Inventory.EntitySpec(type=Inventory.EntitySpec.InventoryType.HOST, hosts=self.entities)
        else:
            print("Not a valid type")
            return

        # Create a spec for transition task
        transition_spec = Inventory.TransitionSpec(entity_spec)
        apiClient = Inventory(self.config)

        # Call the transition task
        task = apiClient.transition_task(transition_spec)

        # If there is any exception that is thrown when waiting for task, return
        if not self.waitForTask(task):
            return

        # Proceed with the rest of the steps
        print("Transition task completed.")
        if (self.entityType.casefold() == "cluster".casefold()):
            clusterClient = Clusters(self.config)
            params = Clusters.GetParams(type=Clusters.GetParams.InventoryType.CLUSTER, clusters=self.entities)

            # Call the cluster summary API to check the transitioned clusters
            cluster_summaries = clusterClient.get(params).cluster_summaries

            # Clusters with status CONVERTED are transitioned, others are not
            print("----------Clusters that are transitioned----------")
            for summary in cluster_summaries:
                if summary.status == Clusters.TransitionStatus.CONVERTED:
                    print("Transitioned Cluster Details ---------- {}", summary)
            print("----------Clusters that are not transitioned----------")
            for summary in cluster_summaries:
                if summary.status is not Clusters.TransitionStatus.CONVERTED:
                    print("Not Transitioned Cluster Details ---------- {}", summary)
        else:
            hostClient = Hosts(self.config)
            params = Hosts.GetParams(type=Hosts.GetParams.InventoryType.HOST, hosts=self.entities)

            # Call the host summary API to check the transitioned hosts
            host_summaries = hostClient.get(params).host_summaries

            # Hosts with status CONVERTED are transitioned, others are not
            print("----------Hosts that are transitioned----------")
            for summary in host_summaries:
                if summary.status == Hosts.TransitionStatus.CONVERTED:
                    print("Transitioned Host Details ---------- {}", summary)
            print("----------Hosts that are not transitioned----------")
            for summary in host_summaries:
                if summary.status is not Hosts.TransitionStatus.CONVERTED:
                    print("Not Transitioned Host Details ---------- {}", summary)

    def waitForTask(self, task):
        i = 0
        try:
            while True:
                i += 1
                status = task.get_info().status
                if status == SUCCEEDED_KEY or status == FAILED_KEY or status == BLOCKED_KEY:
                    return True
                if i > TIME_OUT_ITERATIONS:
                    print("Timeout reached waiting for task--cancelling operation")
                    return False

                time.sleep(1)
        except Exception as e:
            print(f"Error occurred waiting for task: {e}")
            return False


def main():
    bulkTransitionSvc = BulkTransitionSvc()
    bulkTransitionSvc.run()


if __name__ == "__main__":
    main()
