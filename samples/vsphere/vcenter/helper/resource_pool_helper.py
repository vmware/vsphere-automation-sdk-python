"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import ResourcePool

from samples.vsphere.vcenter.helper import datacenter_helper


def get_resource_pool(stub_config, datacenter_name):
    """
    Returns the identifier of the first resourcepool in the datacenter
    """
    datacenter = datacenter_helper.get_datacenter(stub_config, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = ResourcePool.FilterSpec(datacenters=set([datacenter]))

    resource_pool_svc = ResourcePool(stub_config)
    resource_pool_summaries = resource_pool_svc.list(filter_spec)
    if len(resource_pool_summaries) > 0:
        resource_pool = resource_pool_summaries[0].resource_pool
        print("Selecting ResourcePool '{}'".format(resource_pool))
        return resource_pool
    else:
        print("ResourcePool not found in Datacenter '{}'".
              format(datacenter_name))
        return None
