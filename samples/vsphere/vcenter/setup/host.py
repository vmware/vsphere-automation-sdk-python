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
from com.vmware.vcenter_client import (Folder, Host)
from pyVmomi import vim


def detect_host(context, host_name):
    """Find host based on host name"""
    names = set([host_name])

    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))
    if len(host_summaries) > 0:
        host = host_summaries[0].host
        print("Detected Host '{}' as {}".format(host_name, host))
        context.testbed.entities['HOST_IDS'][host_name] = host
        return True
    else:
        print("Host '{}' missing".format(host_name))
        return False


def detect_hosts(context):
    """Find host used to run vcenter samples"""
    context.testbed.entities['HOST_IDS'] = {}
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    return (detect_host(context, host1_name) and
            detect_host(context, host2_name))


def cleanup_hosts(context):
    """Delete hosts after sample run"""
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    names = set([host1_name, host2_name])

    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))
    print('Found {} Hosts matching names {}'.
          format(len(host_summaries), ', '.
                 join(["'{}'".format(n) for n in names])))

    for host_summary in host_summaries:
        host = host_summary.host
        print("Deleting Host '{}' ({})".format(host_summary.name, host))
        context.client.vcenter.Host.delete(host)


def create_host_vapi(context, host_name, datacenter_name):
    """
    Adds a single Host to the vCenter inventory under the named Datacenter
    using vAPI.
    """
    user = context.testbed.config['ESX_USER']
    pwd = context.testbed.config['ESX_PASS']

    # Get the host folder for the Datacenter1 using the folder query
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]
    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.HOST, datacenters=set([datacenter])))
    folder = folder_summaries[0].folder

    create_spec = Host.CreateSpec(
        hostname=host_name,
        user_name=user,
        password=pwd,
        folder=folder,
        thumbprint_verification=Host.CreateSpec.ThumbprintVerification.NONE)
    host = context.client.vcenter.Host.create(create_spec)
    print("Created Host '{}' ({})".format(host, host_name))

    return host


def create_host_vim(context, host_name, datacenter_name):
    """
    Adds a single Host to the vCenter inventory under the named Datacenter
    using the VIM API.
    """
    user = context.testbed.config['ESX_USER']
    pwd = context.testbed.config['ESX_PASS']

    # Get the host folder for the Datacenter1 using the folder query
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    for entity in context.service_instance.content.rootFolder.childEntity:
        if isinstance(entity, vim.Datacenter) and\
                        entity.name == datacenter_name:
            datacenter_mo = entity

    folder_mo = datacenter_mo.hostFolder
    connect_spec = vim.host.ConnectSpec(hostName=host_name,
                                        userName=user,
                                        password=pwd,
                                        force=False)
    print("Creating Host ({})".format(host_name))
    task = folder_mo.AddStandaloneHost(connect_spec,
                                       vim.ComputeResource.ConfigSpec(),
                                       True)
    pyVim.task.WaitForTask(task)

    # Get host from task result
    host_mo = task.info.result.host[0]
    print("Created Host '{}' ({})".format(host_mo._moId, host_name))

    return host_mo._moId


def move_host_into_cluster_vim(context, host_name, cluster_name):
    """Use vim api to move host to another cluster"""
    TIMEOUT = 30  # sec

    host = context.testbed.entities['HOST_IDS'][host_name]
    host_mo = vim.HostSystem(host, context.soap_stub)

    # Move the host into the cluster
    if not host_mo.runtime.inMaintenanceMode:
        task = host_mo.EnterMaintenanceMode(TIMEOUT)
        pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) in maintenance mode".format(host, host_name))

    cluster = context.testbed.entities['CLUSTER_IDS'][cluster_name]
    cluster_mo = vim.ClusterComputeResource(cluster, context.soap_stub)

    task = cluster_mo.MoveInto([host_mo])
    pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) moved into Cluster {} ({})".
          format(host, host_name, cluster, cluster_name))

    task = host_mo.ExitMaintenanceMode(TIMEOUT)
    pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) out of maintenance mode".format(host, host_name))


def setup_hosts_vapi(context):
    """Use vsphere automation API to setup host for sample run"""
    # Create Host1 as a standalone host in Datacenter1
    host1_name = context.testbed.config['ESX_HOST1']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    host1 = create_host_vapi(context, host1_name, datacenter1_name)

    # Create Host2 in a Cluster2
    host2_name = context.testbed.config['ESX_HOST2']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    host2 = create_host_vapi(context, host2_name, datacenter2_name)

    context.testbed.entities['HOST_IDS'] = {
        host1_name: host1,
        host2_name: host2
    }

    # Move Host2 into Cluster2
    cluster_name = context.testbed.config['CLUSTER1_NAME']
    move_host_into_cluster_vim(context, host2_name, cluster_name)


def setup_hosts_vim(context):
    """Use vim API to setup host for sample run"""
    # Create Host1 as a standalone host in Datacenter1
    host1_name = context.testbed.config['ESX_HOST1']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    host1 = create_host_vim(context, host1_name, datacenter1_name)

    # Create Host2 in a Cluster2
    host2_name = context.testbed.config['ESX_HOST2']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    host2 = create_host_vim(context, host2_name, datacenter2_name)

    context.testbed.entities['HOST_IDS'] = {
        host1_name: host1,
        host2_name: host2
    }

    # Move Host2 into Cluster2
    cluster_name = context.testbed.config['CLUSTER1_NAME']
    move_host_into_cluster_vim(context, host2_name, cluster_name)


def setup_hosts(context):
    setup_hosts_vapi(context)


def setup(context):
    setup_hosts(context)


def cleanup(context):
    cleanup_hosts(context)


def validate(context):
    return detect_hosts(context)
