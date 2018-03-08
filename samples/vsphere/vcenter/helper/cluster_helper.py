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
__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import Cluster

from samples.vsphere.vcenter.helper import datacenter_helper


def get_cluster(client, datacenter_name, cluster_name):
    """
    Returns the identifier of a cluster
    Note: The method assumes only one cluster and datacenter
    with the mentioned name.
    """

    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Cluster.FilterSpec(names=set([cluster_name]),
                                     datacenters=set([datacenter]))

    cluster_summaries = client.vcenter.Cluster.list(filter_spec)
    if len(cluster_summaries) > 0:
        cluster = cluster_summaries[0].cluster
        print("Detected cluster '{}' as {}".format(cluster_name, cluster))
        return cluster
    else:
        print("Cluster '{}' not found".format(cluster_name))
        return None
