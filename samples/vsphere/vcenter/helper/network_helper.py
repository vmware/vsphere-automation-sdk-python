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

from com.vmware.vcenter_client import Network

from samples.vsphere.vcenter.helper import datacenter_helper


def get_standard_network_backing(client,
                                 std_porggroup_name,
                                 datacenter_name):
    """
    Gets a standard portgroup network backing for a given Datacenter
    Note: The method assumes that there is only one standard portgroup
    and datacenter with the mentioned names.
    """
    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter = Network.FilterSpec(datacenters=set([datacenter]),
                                names=set([std_porggroup_name]),
                                types=set([Network.Type.STANDARD_PORTGROUP]))
    network_summaries = client.vcenter.Network.list(filter=filter)

    if len(network_summaries) > 0:
        network = network_summaries[0].network
        print("Selecting Standard Portgroup Network '{}' ({})".
              format(std_porggroup_name, network))
        return network
    else:
        print("Standard Portgroup Network not found in Datacenter '{}'".
              format(datacenter_name))
        return None


def get_distributed_network_backing(client,
                                    dv_portgroup_name,
                                    datacenter_name):
    """
    Gets a distributed portgroup network backing for a given Datacenter
    Note: The method assumes that there is only one distributed portgroup
    and datacenter with the mentioned names.
    """
    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter = Network.FilterSpec(datacenters=set([datacenter]),
                                names=set([dv_portgroup_name]),
                                types=set([Network.Type.DISTRIBUTED_PORTGROUP]))
    network_summaries = client.vcenter.Network.list(filter=filter)

    if len(network_summaries) > 0:
        network = network_summaries[0].network
        print("Selecting Distributed Portgroup Network '{}' ({})".
              format(dv_portgroup_name, network))
        return network
    else:
        print("Distributed Portgroup Network not found in Datacenter '{}'".
              format(datacenter_name))
        return None
