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

from com.vmware.vcenter_client import ResourcePool

from samples.vsphere.vcenter.helper import datacenter_helper


def get_resource_pool(client, datacenter_name, resource_pool_name=None):
    """
    Returns the identifier of the resource pool with the given name or the
    first resource pool in the datacenter if the name is not provided.
    """
    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    names = set([resource_pool_name]) if resource_pool_name else None
    filter_spec = ResourcePool.FilterSpec(datacenters=set([datacenter]),
                                          names=names)

    resource_pool_summaries = client.vcenter.ResourcePool.list(filter_spec)
    if len(resource_pool_summaries) > 0:
        resource_pool = resource_pool_summaries[0].resource_pool
        print("Selecting ResourcePool '{}'".format(resource_pool))
        return resource_pool
    else:
        print("ResourcePool not found in Datacenter '{}'".
              format(datacenter_name))
        return None
