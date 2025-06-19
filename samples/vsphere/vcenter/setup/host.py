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


def detect_host(context, host_ip):
    """Find host based on host name"""
    names = set([host_ip])

    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))
    if len(host_summaries) > 0:
        host = host_summaries[0].host
        print("Detected Host '{}' as {}".format(host_ip, host))
        context.testbed.entities['HOST_IDS'][host_ip] = host
        return True
    else:
        print("Host '{}' missing".format(host_ip))
        return False


def detect_hosts(context):
    """Find host used to run vcenter samples"""
    context.testbed.entities['HOST_IDS'] = {}
    host1_ip = context.testbed.config['ESX1_HOST']
    host2_ip = context.testbed.config['ESX2_HOST']
    return (detect_host(context, host1_ip) and
            detect_host(context, host2_ip))


def cleanup_hosts(context):
    """Delete hosts after sample run"""
    host1_name = context.testbed.config['ESX1_HOST']
    host2_name = context.testbed.config['ESX2_HOST']
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


def create_host_vapi(context, host_user, host_pwd, host_ip, datacenter_name):
    """
    Adds a single Host to the vCenter inventory under the named Datacenter
    using vAPI.
    """
    # Get the host folder for the Datacenter1 using the folder query
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]
    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.HOST, datacenters=set([datacenter])))
    folder = folder_summaries[0].folder

    create_spec = Host.CreateSpec(
        hostname=host_ip,
        user_name=host_user,
        password=host_pwd,
        folder=folder,
        thumbprint_verification=Host.CreateSpec.ThumbprintVerification.NONE)
    host = context.client.vcenter.Host.create(create_spec)
    print("Created Host '{}' ({})".format(host, host_ip))

    return host


def create_host_vim(context, host_user, host_pwd, host_ip, datacenter_name):
    """
    Adds a single Host to the vCenter inventory under the named Datacenter
    using the VIM API.
    """
    # Get the host folder for the Datacenter1 using the folder query
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]

    for entity in context.service_instance.content.rootFolder.childEntity:
        if isinstance(entity, vim.Datacenter) and\
                        entity.name == datacenter_name:
            datacenter_mo = entity

    folder_mo = datacenter_mo.hostFolder
    connect_spec = vim.host.ConnectSpec(hostName=host_ip,
                                        userName=host_user,
                                        password=host_pwd,
                                        force=False)
    print("Creating Host ({})".format(host_ip))
    task = folder_mo.AddStandaloneHost(connect_spec,
                                       vim.ComputeResource.ConfigSpec(),
                                       True)
    pyVim.task.WaitForTask(task)

    # Get host from task result
    host_mo = task.info.result.host[0]
    print("Created Host '{}' ({})".format(host_mo._moId, host_ip))

    return host_mo._moId


def move_host_into_cluster_vim(context, host_ip, cluster_name):
    """Use vim api to move host to another cluster"""
    TIMEOUT = 30  # sec

    host = context.testbed.entities['HOST_IDS'][host_ip]
    host_mo = vim.HostSystem(host, context.soap_stub)

    # Move the host into the cluster
    if not host_mo.runtime.inMaintenanceMode:
        task = host_mo.EnterMaintenanceMode(TIMEOUT)
        pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) in maintenance mode".format(host, host_ip))

    cluster = context.testbed.entities['CLUSTER_IDS'][cluster_name]
    cluster_mo = vim.ClusterComputeResource(cluster, context.soap_stub)

    task = cluster_mo.MoveInto([host_mo])
    pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) moved into Cluster {} ({})".
          format(host, host_ip, cluster, cluster_name))

    task = host_mo.ExitMaintenanceMode(TIMEOUT)
    pyVim.task.WaitForTask(task)
    print("Host '{}' ({}) out of maintenance mode".format(host, host_ip))


def setup_hosts_vapi(context):
    """Use vsphere automation API to setup host for sample run"""
    # Create Host1 as a standalone host in Datacenter1
    host1_ip = context.testbed.config['ESX1_HOST']
    host1_user = context.testbed.config['ESX1_USER']
    host1_pwd = context.testbed.config['ESX1_PWD']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    host1 = create_host_vapi(context, host1_user, host1_pwd, host1_ip, datacenter1_name)

    # Create Host2 in a Cluster2
    host2_ip = context.testbed.config['ESX2_HOST']
    host2_user = context.testbed.config['ESX2_USER']
    host2_pwd = context.testbed.config['ESX2_PWD']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    host2 = create_host_vapi(context, host2_user, host2_pwd, host2_ip, datacenter2_name)

    context.testbed.entities['HOST_IDS'] = {
        host1_ip: host1,
        host2_ip: host2
    }

    # Move Host2 into Cluster2
    cluster_name = context.testbed.config['CLUSTER1_NAME']
    move_host_into_cluster_vim(context, host2_ip, cluster_name)


def setup_hosts_vim(context):
    """Use vim API to setup host for sample run"""
    # Create Host1 as a standalone host in Datacenter1
    host1_ip = context.testbed.config['ESX1_HOST']
    host1_user = context.testbed.config['ESX1_USER']
    host1_pwd = context.testbed.config['ESX1_PWD']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    host1 = create_host_vim(context, host1_user, host1_pwd, host1_ip, datacenter1_name)

    # Create Host2 in a Cluster2
    host2_ip = context.testbed.config['ESX2_HOST']
    host2_user = context.testbed.config['ESX2_USER']
    host2_pwd = context.testbed.config['ESX2_PWD']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    host2 = create_host_vim(context, host2_user, host2_pwd, host2_ip, datacenter2_name)

    context.testbed.entities['HOST_IDS'] = {
        host1_ip: host1,
        host2_ip: host2
    }

    # Move Host2 into Cluster2
    cluster_name = context.testbed.config['CLUSTER1_NAME']
    move_host_into_cluster_vim(context, host2_ip, cluster_name)


def setup_hosts(context):
    setup_hosts_vapi(context)


def setup(context):
    setup_hosts(context)


def cleanup(context):
    cleanup_hosts(context)


def validate(context):
    return detect_hosts(context)
