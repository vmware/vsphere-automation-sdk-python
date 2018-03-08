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

from com.vmware.vcenter_client import Datastore

from samples.vsphere.vcenter.helper import datacenter_helper


def get_datastore(client, datacenter_name, datastore_name):
    """
    Returns the identifier of a datastore
    Note: The method assumes that there is only one datastore and datacenter
    with the mentioned names.
    """
    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Datastore.FilterSpec(names=set([datastore_name]),
                                       datacenters=set([datacenter]))

    datastore_summaries = client.vcenter.Datastore.list(filter_spec)
    if len(datastore_summaries) > 0:
        datastore = datastore_summaries[0].datastore
        return datastore
    else:
        return None
