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

from com.vmware.vcenter_client import Datacenter


def get_datacenter(client, datacenter_name):
    """
    Returns the identifier of a datacenter
    Note: The method assumes only one datacenter with the mentioned name.
    """

    filter_spec = Datacenter.FilterSpec(names=set([datacenter_name]))

    datacenter_summaries = client.vcenter.Datacenter.list(filter_spec)
    if len(datacenter_summaries) > 0:
        datacenter = datacenter_summaries[0].datacenter
        return datacenter
    else:
        return None
