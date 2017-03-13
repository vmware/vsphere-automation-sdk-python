"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import (Cluster, Datastore, Folder, ResourcePool,
                                       VM)

from samples.vsphere.vcenter.helper import vm_placement_helper


#####################################################################
# Placement samples: How to get a valid PlacementSpec to create a VM
#####################################################################

# Place to a Cluster
#
#   a. Datacenter based flow:
#      * Use vcenter.Datacenter#list() to find a datacenter
#      * Find a compute resource that is in the selected Datacenter
#        * 1. Cluster:
#             * Use the cluster list operation to find a cluster in a
# datacenter with a specific name
#

def get_placement_spec_for_cluster(context):
    """
    Cluster names are not guaranteed to be unique within a vCenter instance,
    so we qualify our search using the Datacenter.  If Folders are used, the
    search must be qualified using Folders since a Cluster name is not
    guaranteed to be unique across different Folders within a Datacenter.
    """
    # Select a Cluster meeting our requirements
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    cluster_name = context.testbed.config['CLUSTER1_NAME']
    names = set([cluster_name])

    cluster_svc = Cluster(context.stub_config)
    filter = Cluster.FilterSpec(
        names=set([cluster_name]),
        datacenters=set([datacenter]))
    cluster_summaries = cluster_svc.list(filter=filter)

    cluster = None
    if len(cluster_summaries) > 0:
        cluster = cluster_summaries[0].cluster
        print("Selecting Cluster '{}' ({})".format(cluster_name, cluster))
    else:
        print("Cluster '{}' not found".format(cluster_name))
        return None

    # Select a Folder meeting our requirements.
    #
    # Must be in the same Datacenter as the Cluster that was chosen.
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    folder_name = context.testbed.config['VM_FOLDER2_NAME']

    folder_svc = Folder(context.stub_config)
    filter = Folder.FilterSpec(
        names=set([folder_name]),
        datacenters=set([datacenter]))
    folder_summaries = folder_svc.list(filter=filter)

    folder = None
    if len(folder_summaries) > 0:
        folder = folder_summaries[0].folder
        print("Selecting Folder '{}' ({})".format(folder_name, folder))
    else:
        print("Folder '{}' not found".format(folder_name))
        return None

    # Select a Datastore meeting our requirements.
    #
    # Must be in the same Datacenter as the Cluster that was chosen.
    # TODO No way to validate that Cluster is connected to Datastore
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    # TODO Parameterize based on NFS or VMFS
    datastore_name = context.testbed.config['NFS_DATASTORE_NAME']

    datastore_svc = Datastore(context.stub_config)
    filter = Datastore.FilterSpec(
        names=set([datastore_name]),
        datacenters=set([datacenter]))
    datastore_summaries = datastore_svc.list(filter=filter)

    datastore = None
    if len(datastore_summaries) > 0:
        datastore = datastore_summaries[0].datastore
        print("Selecting Datastore '{}' ({})".format(datastore_name, datastore))
    else:
        print("Datastore '{}' not found".format(datastore_name))
        return None

    placement_spec = VM.PlacementSpec(folder=folder,
                                      cluster=cluster,
                                      datastore=datastore)
    print("get_placement_spec_for_cluster: Result is '{}'".
          format(placement_spec))
    return placement_spec


def get_placement_spec_for_resource_pool(context):
    # Select a ResourcePool meeting our requirements
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    resource_pool_svc = ResourcePool(context.stub_config)
    filter = ResourcePool.FilterSpec(datacenters=set([datacenter]))
    resource_pool_summaries = resource_pool_svc.list(filter=filter)

    resource_pool = None
    if len(resource_pool_summaries) > 0:
        resource_pool = resource_pool_summaries[0].resource_pool
        print('Selecting ResourcePool ({})'.format(resource_pool))
    else:
        print("ResourcePool not found in Datacenter '{}'".
              format(datacenter_name))
        return None

    # Select a Folder meeting our requirements.
    #
    # Must be in the same Datacenter as the ResourcePool that was chosen.
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    folder_name = context.testbed.config['VM_FOLDER2_NAME']

    folder_svc = Folder(context.stub_config)
    filter = Folder.FilterSpec(
        names=set([folder_name]),
        datacenters=set([datacenter]))
    folder_summaries = folder_svc.list(filter=filter)

    folder = None
    if len(folder_summaries) > 0:
        folder = folder_summaries[0].folder
        print("Selecting Folder '{}' ({})".format(folder_name, folder))
    else:
        print("Folder '{}' not found".format(folder_name))
        return None

    # Select a Datastore meeting our requirements.
    #
    # Must be in the same Datacenter as the ResourcePool that was chosen.
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    # TODO Parameterize based on NFS or VMFS
    datastore_name = context.testbed.config['NFS_DATASTORE_NAME']

    datastore_svc = Datastore(context.stub_config)
    filter = Datastore.FilterSpec(
        names=set([datastore_name]),
        datacenters=set([datacenter]))
    datastore_summaries = datastore_svc.list(filter=filter)

    datastore = None
    if len(datastore_summaries) > 0:
        datastore = datastore_summaries[0].datastore
        print("Selecting Datastore '{}' ({})".format(datastore_name, datastore))
    else:
        print("Datastore '{}' not found".format(datastore_name))
        return None

    placement_spec = VM.PlacementSpec(folder=folder,
                                      resource_pool=resource_pool,
                                      datastore=datastore)
    print("get_placement_spec_for_resourcepool: Result is '{}'".
          format(placement_spec))
    return placement_spec
