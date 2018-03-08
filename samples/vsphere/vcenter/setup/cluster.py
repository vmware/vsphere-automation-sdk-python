"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
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

import pyVim.task
from com.vmware.vcenter_client import Cluster, Folder
from pyVmomi import vim

from samples.vsphere.vcenter.helper import cluster_helper


def detect_cluster(context):
    """Find the cluster to run the vcenter samples"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']
    datacenter_name = context.testbed.config['VM_DATACENTER_NAME']

    cluster = cluster_helper.get_cluster(context.client, datacenter_name,
                                         cluster1_name)

    if cluster:
        context.testbed.entities['CLUSTER_IDS'] = {}
        context.testbed.entities['CLUSTER_IDS'][cluster1_name] = cluster
        return True
    else:
        return False


def cleanup_cluster(context):
    """Delete cluster after vcenter sample run"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']
    names = set([cluster1_name])

    cluster_summaries = context.client.vcenter.Cluster.list(
        Cluster.FilterSpec(names=names))
    print("Found '{}' Clusters matching names {}".
          format(len(cluster_summaries), ", ".join(["'{}'".
                                                   format(n) for n in names])))

    if len(cluster_summaries) < 1:
        return

    # Delete the cluster using the managed object
    cluster = cluster_summaries[0].cluster
    cluster_mo = vim.ClusterComputeResource(cluster, context.soap_stub)

    print("Deleting Cluster '{}' ({})".format(cluster, cluster1_name))
    task = cluster_mo.Destroy()
    pyVim.task.WaitForTask(task)


def setup_cluster_vapi1(context):
    """Create a cluster from the Datacenter managed object."""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']

    # Get the host folder for the Datacenter2 using the save identifier
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    # Create a managed object from the datacenter identifier
    datacenter_mo = vim.Datacenter(datacenter, context.soap_stub)

    # Using pyvmomi to get the host folder on which to create the cluster
    folder_mo = datacenter_mo.hostFolder
    cluster_mo = folder_mo.CreateClusterEx(cluster1_name,
                                           vim.cluster.ConfigSpecEx())

    print("Created Cluster '{}' ({})".format(cluster_mo._moId, cluster1_name))

    context.testbed.entities['CLUSTER_IDS'] = {
        cluster1_name: cluster_mo._moId
    }


def setup_cluster_vapi2(context):
    """Create a cluster from the Folder managed object"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']

    # Get the host folder for the Datacenter2 using the folder query
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.HOST, datacenters=set([datacenter])))
    folder = folder_summaries[0].folder

    # Create a managed object from the folder identifier
    folder_mo = vim.Folder(folder, context.soap_stub)
    cluster_mo = folder_mo.CreateClusterEx(cluster1_name,
                                           vim.cluster.ConfigSpecEx())

    print("Created Cluster '{}' ({})".format(cluster_mo._moId, cluster1_name))

    context.testbed.entities['CLUSTER_IDS'] = {
        cluster1_name: cluster_mo._moId
    }


def setup_cluster_vim(context):
    """Create a cluster using only the VIM API"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']

    # Get the host folder for the Datacenter2 using the save identifier
    datacenter_name = context.testbed.config['DATACENTER2_NAME']

    for entity in context.service_instance.content.rootFolder.childEntity:
        if isinstance(entity,
                      vim.Datacenter) and entity.name == datacenter_name:
            folder_mo = entity.hostFolder
            cluster_mo = folder_mo.CreateClusterEx(cluster1_name,
                                                   vim.cluster.ConfigSpecEx())

            print("Created Cluster '{}' ({})".format(cluster_mo._moId,
                                                     cluster1_name))

            context.testbed.entities['CLUSTER_IDS'] = {
                cluster1_name: cluster_mo._moId
            }
            break


def setup_cluster(context):
    setup_cluster_vim(context)


def setup(context):
    setup_cluster(context)


def cleanup(context):
    cleanup_cluster(context)


def validate(context):
    return detect_cluster(context)
