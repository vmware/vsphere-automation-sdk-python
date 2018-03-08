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
__vcenter__ = 'since 6.0'

from pyVmomi import vim

from samples.vsphere.vcenter.helper.datastore_helper import get_datastore


def get_datastore_mo(client, soap_stub,
                     datacenter_name, datastore_name):
    """
    Return datastore managed object with specific datacenter and datastore name
    """
    datastore = get_datastore(client, datacenter_name, datastore_name)
    if not datastore:
        return None
    datastore_mo = vim.Datastore(datastore, soap_stub)
    return datastore_mo


# TODO Not the most efficient implementation.  This can be done as a single
# property collector query but it's a little more complicated
def get_datacenter_for_datastore(datastore_mo):
    datacenter_mo = datastore_mo.parent
    while datacenter_mo is not None:
        if isinstance(datacenter_mo, vim.Datacenter):
            return datacenter_mo
        datacenter_mo = datacenter_mo.parent
    return None
