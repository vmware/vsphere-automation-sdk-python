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
from com.vmware.vcenter_client import Host
from pyVmomi import vim


def detect_nfs_datastore_on_host(context, host_name):
    """Find NFS datastore on host"""
    names = set([host_name])
    datastore_name = context.testbed.config['NFS_DATASTORE_NAME']

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if (datastore_mo.name == datastore_name and
                datastore_mo.summary.type == 'NFS'):
                datastore = datastore_mo._moId
                print("Detected NFS Volume '{}' as {} on Host '{}' ({})".
                      format(datastore_name, datastore, host_name, host))
                context.testbed.entities['HOST_NFS_DATASTORE_IDS'][host_name] \
                    = datastore
                return True

    print("NFS Volume '{}' missing on Host '{}'".
          format(datastore_name, host_name))
    return False


def detect_nfs_datastore(context):
    """Find NFS datastore used to run vcenter samples"""
    context.testbed.entities['HOST_NFS_DATASTORE_IDS'] = {}
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    return (detect_nfs_datastore_on_host(context, host1_name) and
            detect_nfs_datastore_on_host(context, host2_name))


def cleanup_nfs_datastore(context):
    """Cleanup NFS datastore after running vcenter samples"""
    # Remove NFS datastore from each Host
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    names = set([host1_name, host2_name])

    datastore_name = context.testbed.config['NFS_DATASTORE_NAME']

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if datastore_mo.name == datastore_name:
                datastore_system = host_mo.configManager.datastoreSystem
                datastore_system.RemoveDatastore(datastore_mo)
                print("Removed NFS Volume '{}' ({}) from Host '{}' ({})".
                      format(datastore_name, datastore_mo._moId,
                             host_mo.name, host_mo._moId))

                # Remote NFS Datastore at the vCenter level
                # TODO Do we need to do this?


def setup_nfs_datastore(context):
    """Setup NFS datastore for running vcenter samples"""
    host1_name = context.testbed.config['ESX_HOST1']
    nfs_datastore1 = setup_nfs_datastore_on_host(context, host1_name)

    host2_name = context.testbed.config['ESX_HOST2']
    nfs_datastore2 = setup_nfs_datastore_on_host(context, host2_name)

    context.testbed.entities['HOST_NFS_DATASTORE_IDS'] = {
        host1_name: nfs_datastore1,
        host2_name: nfs_datastore2
    }


def setup_nfs_datastore_on_host(context, host_name):
    """Mount the NFS volume on one ESX hosts using the VIM API."""
    nfs_host = context.testbed.config['NFS_HOST']
    remote_path = context.testbed.config['NFS_REMOTE_PATH']
    local_path = context.testbed.config['NFS_DATASTORE_NAME']

    host = context.testbed.entities['HOST_IDS'][host_name]
    host_mo = vim.HostSystem(host, context.soap_stub)

    datastore_system = host_mo.configManager.datastoreSystem
    try:
        datastore_mo = datastore_system.CreateNasDatastore(
            vim.host.NasVolume.Specification(remoteHost=nfs_host,
                                             remotePath=remote_path,
                                             localPath=local_path,
                                             accessMode=vim.host.MountInfo.AccessMode.readWrite,
                                             type=vim.host.FileSystemVolume.FileSystemType.NFS))

        print("Added NFS Volume '{}' ({}) to Host '{}' ({})".
              format(local_path, datastore_mo._moId, host_name, host))
        return datastore_mo._moId
    except vim.fault.AlreadyExists as e:
        print("NFS Volume '{}' already exists on Host '{}' ({})".
              format(local_path, host_name, host))
        for datastore_mo in host_mo.datastore:
            info = datastore_mo.info
            if (isinstance(info, vim.host.NasDatastoreInfo) and
                           info.nas.remoteHost == nfs_host and
                           info.nas.remotePath == remote_path):
                if info.name == local_path:
                    print("Found NFS Volume '{}' ({}) on Host '{}' ({})".
                          format(local_path, datastore_mo._moId,
                                 host_name, host_mo._moId))
                    return datastore_mo._moId
                else:
                    print("Found NFS remote host '{}' and path '{}' on Host '{}' ({}) as '{}'".
                          format(nfs_host, remote_path, host_name,
                                 host_mo._moId, info.name))

                    print("Renaming NFS Volume '{}' ({}) to '{}'".
                          format(info.name, datastore_mo._moId, local_path))
                    task = datastore_mo.Rename(local_path)
                    pyVim.task.WaitForTask(task)

        # TODO Find the datastore identifier for the NFS volume and return it
        return None


def detect_vmfs_datastore(context, host_name, datastore_name):
    """Find VMFS datastore given host and datastore names"""
    names = set([host_name])

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if (datastore_mo.name == datastore_name and
                datastore_mo.summary.type == 'VMFS'):
                datastore = datastore_mo._moId
                print("Detected VMFS Volume '{}' as {} on Host '{}' ({})".
                      format(datastore_name, datastore, host_name, host))
                context.testbed.entities['HOST_VMFS_DATASTORE_IDS'][host_name] \
                    = datastore
                return True

    print("VMFS Volume '{}' missing on Host '{}'".
          format(datastore_name, host_name))
    return False


def detect_vmfs_datastores(context):
    """Find VMFS datastore used to run vcenter samples"""
    context.testbed.entities['HOST_VMFS_DATASTORE_IDS'] = {}

    host1_name = context.testbed.config['ESX_HOST1']
    host1_vmfs_volume = context.testbed.config['ESX_HOST1_VMFS_DATASTORE']

    host2_name = context.testbed.config['ESX_HOST2']
    host2_vmfs_volume = context.testbed.config['ESX_HOST2_VMFS_DATASTORE']

    # From each host, look for the VMFS Volume
    return (detect_vmfs_datastore(context, host1_name, host1_vmfs_volume) and
            detect_vmfs_datastore(context, host2_name, host2_vmfs_volume))


def setup_vmfs_datastore(context, host_name, datastore_name):
    """Find VMFS datastore given host and datastore names"""
    context.testbed.entities['HOST_VMFS_DATASTORE_IDS'] = {}

    names = set([host_name])

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    host_summary = host_summaries[0]
    # Convert the host identifier into a ManagedObject
    host = host_summary.host
    host_mo = vim.HostSystem(host, context.soap_stub)

    vmfs_datastores = dict([(datastore_mo.name, datastore_mo)
                            for datastore_mo in host_mo.datastore
                            if datastore_mo.summary.type == 'VMFS'])

    # The VMFS volume exists.  No need to do anything
    if datastore_name in vmfs_datastores:
        datastore = vmfs_datastores[datastore_name]._moId
        print("Detected VMFS Volume '{}' as {} on Host '{}' ({})".
              format(datastore_name, datastore, host_name, host))
        context.testbed.entities['HOST_VMFS_DATASTORE_IDS'][host_name] \
            = datastore
        return True

    # Rename a VMFS datastore
    if len(vmfs_datastores) > 0:
        datastore_mo = list(vmfs_datastores.values())[0]
        datastore = datastore_mo._moId
        print("Renaming VMFS Volume '{}' ({}) on Host '{}' ({}) to '{}'".
              format(datastore_mo.name, datastore,
                     host_name, host, datastore_name))
        task = datastore_mo.Rename(datastore_name)
        pyVim.task.WaitForTask(task)
        return True

    return False


def setup_vmfs_datastores(context):
    """Setup VMFS datastore used to run vcenter samples"""
    host1_name = context.testbed.config['ESX_HOST1']
    host1_vmfs_volume = context.testbed.config['ESX_HOST1_VMFS_DATASTORE']

    host2_name = context.testbed.config['ESX_HOST2']
    host2_vmfs_volume = context.testbed.config['ESX_HOST2_VMFS_DATASTORE']

    # From each host, look for the VMFS Volume
    setup_vmfs_datastore(context, host1_name, host1_vmfs_volume)
    setup_vmfs_datastore(context, host2_name, host2_vmfs_volume)


def setup(context):
    setup_nfs_datastore(context)
    setup_vmfs_datastores(context)


def cleanup(context):
    cleanup_nfs_datastore(context)


def validate(context):
    return (
        detect_nfs_datastore(context) and
        detect_vmfs_datastores(context))
