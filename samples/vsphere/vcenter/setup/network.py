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


def detect_vdswitches(context):
    """Find distributed virtual switch used to run vcenter samples"""
    context.testbed.entities['DISTRIBUTED_SWITCH_IDS'] = {}
    context.testbed.entities['DISTRIBUTED_PORTGROUP_IDS'] = {}

    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    vdswitch_name = context.testbed.config['VDSWITCH1_NAME']
    vdswitch_mo = find_vdswitch(context, datacenter_name, vdswitch_name)
    if vdswitch_mo:
        vdswitch = vdswitch_mo._moId
        print("Detected Distributed Switch '{}' as {}".
              format(vdswitch_name, vdswitch))
        context.testbed.entities['DISTRIBUTED_SWITCH_IDS'][
            vdswitch_name] = vdswitch

        vdportgroup_name = context.testbed.config['VDPORTGROUP1_NAME']
        vdportgroup_mo = find_vdportgroup(context, datacenter_name,
                                          vdswitch_name, vdportgroup_name)
        if vdportgroup_mo:
            vdportgroup = vdportgroup_mo._moId
            print("Detected Distributed Portgroup '{}' as {}".
                  format(vdportgroup_name, vdportgroup))
            context.testbed.entities['DISTRIBUTED_PORTGROUP_IDS'][
                vdportgroup_name] = vdportgroup
        else:
            print("Distributed Portgroup '{}' missing".format(vdportgroup_name))
            return False
    else:
        print("Distributed Switch '{}' missing".format(vdswitch_name))
        return False
    return True


def cleanup_vdswitch(context):
    """Cleanup Distributed Switch after sampel run"""
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    vdswitch_name = context.testbed.config['VDSWITCH1_NAME']
    vdswitch_mo = find_vdswitch(context, datacenter_name, vdswitch_name)
    if vdswitch_mo:
        vdportgroup_name = context.testbed.config['VDPORTGROUP1_NAME']
        vdportgroup_mo = find_vdportgroup(context, datacenter_name,
                                          vdswitch_name, vdportgroup_name)

        if vdportgroup_mo:
            print("Deleting Distributed Portgroup '{}' ({})".
                  format(vdportgroup_name, vdportgroup_mo._moId))
            task = vdportgroup_mo.Destroy()
            pyVim.task.WaitForTask(task)

            host_name = context.testbed.config['ESX_HOST2']
            remove_host_from_vdswitch(context, vdswitch_mo, host_name)

        print("Deleting Distributed Switch '{}' ({})".
              format(vdswitch_name, vdswitch_mo._moId))
        task = vdswitch_mo.Destroy()
        pyVim.task.WaitForTask(task)


def find_vdswitch(context, datacenter_name, vdswitch_name):
    """ Retrieve an existing Distributed Switch"""
    # TODO Ugly deep nesting.
    for datacenter_mo in context.service_instance.content.rootFolder \
            .childEntity:
        if (isinstance(datacenter_mo, vim.Datacenter) and
                    datacenter_mo.name == datacenter_name):
            for vdswitch_mo in datacenter_mo.networkFolder.childEntity:
                if (isinstance(vdswitch_mo, vim.DistributedVirtualSwitch) and
                            vdswitch_mo.summary.name == vdswitch_name):
                    print("Found VDSwitch '{}' ({}) in Datacenter '{}' ({})".
                          format(vdswitch_name, vdswitch_mo._moId,
                                 datacenter_name, datacenter_mo._moId))
                    return vdswitch_mo
    return None


def find_vdportgroup(context, datacenter_name, vdswitch_name, vdportgroup_name):
    """
    Find existing Distributed Switch portgroup based on datacenter,
    vds name and portgroup name
    """
    vdswitch_mo = find_vdswitch(context, datacenter_name, vdswitch_name)
    for vdportgroup_mo in vdswitch_mo.portgroup:
        if vdportgroup_mo.name == vdportgroup_name:
            print(
                "Found Distributed Portgroup '{}' ({}) on Distributed Switch '{}' ({})".
                format(vdportgroup_name, vdportgroup_mo._moId,
                       vdswitch_name, vdswitch_mo._moId))
            return vdportgroup_mo
    return None


def create_vdswitch(context, datacenter_name, vdswitch_name):
    """Create Distributed Switch in given datacenter"""
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]
    datacenter_mo = vim.Datacenter(datacenter, context.soap_stub)

    spec = vim.DistributedVirtualSwitch.CreateSpec()
    spec.configSpec = vim.DistributedVirtualSwitch.ConfigSpec(
        name=vdswitch_name)

    task = datacenter_mo.networkFolder.CreateDistributedVirtualSwitch(spec)
    pyVim.task.WaitForTask(task)
    vdswitch_mo = task.info.result
    print("Created Distributed Switch '{}' ({})".
          format(vdswitch_name, vdswitch_mo._moId))
    return vdswitch_mo._moId


def create_vdportgroup(context, vdswitch_name, vdportgroup_name):
    """Create Distributed Switch portgroup"""
    vdportgroup_type = "earlyBinding"

    vdswitch = context.testbed.entities['DISTRIBUTED_SWITCH_IDS'][vdswitch_name]
    vdswitch_mo = vim.DistributedVirtualSwitch(vdswitch, context.soap_stub)

    vdportgroup_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec(
        name=vdportgroup_name, type=vdportgroup_type)
    vdportgroup_specs = [vdportgroup_spec]

    task = vdswitch_mo.AddPortgroups(vdportgroup_specs)
    pyVim.task.WaitForTask(task)

    # The AddPortgroup operation doesn't return any information about the
    # created portgroup, so look it up.
    vdportgroup = None
    for vdportgroup_mo in vdswitch_mo.portgroup:
        if vdportgroup_mo.name == vdportgroup_name:
            vdportgroup = vdportgroup_mo._moId
            print(
                "Created Distributed Portgroup '{}' ({}) on Distributed Switch '{}' ({})".
                format(vdportgroup_name, vdportgroup, vdswitch_name, vdswitch))
    return vdportgroup


def add_host_to_vdswitch(context, vdswitch_name, host_name, pnic_names=None):
    """Add host to Distributed Switch"""
    host = context.testbed.entities['HOST_IDS'][host_name]
    host_mo = vim.HostSystem(host, context.soap_stub)

    vdswitch = context.testbed.entities['DISTRIBUTED_SWITCH_IDS'][vdswitch_name]
    vdswitch_mo = vim.DistributedVirtualSwitch(vdswitch, context.soap_stub)

    pnic_specs = []
    if pnic_names:
        for pnic in pnic_names:
            pnic_specs.append(vim.dvs.HostMember.PnicSpec(pnicDevice=pnic))

    dvs_member_config = vim.dvs.HostMember.ConfigSpec(
        operation="add",
        host=host_mo,
        backing=vim.dvs.HostMember.PnicBacking(pnicSpec=pnic_specs))

    dvs_config = vim.DistributedVirtualSwitch.ConfigSpec(
        configVersion=vdswitch_mo.config.configVersion,
        host=[dvs_member_config])

    task = vdswitch_mo.Reconfigure(dvs_config)
    pyVim.task.WaitForTask(task)

    print("Added Host '{}' ({}) to Distributed Switch '{}' ({})".
          format(host_name, host, vdswitch_name, vdswitch))


def remove_host_from_vdswitch(context, vdswitch_mo, host_name):
    """Remove host from Distributed Switch"""
    for host_member in vdswitch_mo.config.host:
        if host_member.config.host.name == host_name:
            dvs_member_config = vim.dvs.HostMember.ConfigSpec(
                operation="remove",
                host=host_member.config.host)

            dvs_config = vim.DistributedVirtualSwitch.ConfigSpec(
                configVersion=vdswitch_mo.config.configVersion,
                host=[dvs_member_config])

            task = vdswitch_mo.Reconfigure(dvs_config)
            pyVim.task.WaitForTask(task)

            print("Removed Host '{}' ({}) from Distributed Switch '{}' ({})".
                  format(host_name, host_member.config.host._moId,
                         vdswitch_mo.summary.name, vdswitch_mo._moId))


def setup_vdswitch(context):
    """Setup Distributed Switch used to run vcenter samples"""
    # Add a Distributed Switch
    datacenter_name = context.testbed.config['DATACENTER2_NAME']
    vdswitch1_name = context.testbed.config['VDSWITCH1_NAME']
    vdswitch1 = create_vdswitch(context, datacenter_name, vdswitch1_name)

    context.testbed.entities['DISTRIBUTED_SWITCH_IDS'] = {
        vdswitch1_name: vdswitch1
    }

    # Add a Distributed Portgroup
    vdportgroup1_name = context.testbed.config['VDPORTGROUP1_NAME']
    vdportgroup1 = create_vdportgroup(context, vdswitch1_name,
                                      vdportgroup1_name)

    context.testbed.entities['DISTRIBUTED_PORTGROUP_IDS'] = {
        vdportgroup1_name: vdportgroup1
    }

    # Add a Host into the Distributed Switch
    host2_name = context.testbed.config['ESX_HOST2']
    add_host_to_vdswitch(context, vdswitch1_name, host2_name)

    # @TODO: Add Host Uplink


def detect_stdportgroup(context, host_name, network_name):
    """Find Distributed Switch based on host and network name"""
    # Ensure the standard switch is available on the host
    names = set([host_name])

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for network_mo in host_mo.network:
            if (type(network_mo) == vim.Network and
                        network_mo.name == network_name):
                network = network_mo._moId
                print(
                    "Detected Standard Portgroup '{}' as {} on Host '{}' ({})".
                    format(network_name, network, host_name, host))
                context.testbed.entities['HOST_STANDARD_SWITCH_IDS'][
                    host_name] = network
                return True

    print("Standard Portgroup '{}' missing on Host '{}'".
          format(network_name, host_name))
    return False


def detect_stdportgroups(context):
    """Find Distributed Switch used to run vcenter samples"""
    context.testbed.entities['HOST_STANDARD_SWITCH_IDS'] = {}
    network_name = context.testbed.config['STDPORTGROUP_NAME']
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    return (detect_stdportgroup(context, host1_name, network_name) and
            detect_stdportgroup(context, host2_name, network_name))


def setup(context):
    setup_vdswitch(context)


def cleanup(context):
    cleanup_vdswitch(context)


def validate(context):
    return (
        detect_vdswitches(context) and
        detect_stdportgroups(context))
