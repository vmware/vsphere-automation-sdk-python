"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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

from com.vmware.vcenter_client import Datacenter


def get_datacenter(stub_config, datacenter_name):
    """
    Returns the identifier of a datacenter
    Note: The method assumes only one datacenter with the mentioned name.
    """

    filter_spec = Datacenter.FilterSpec(names=set([datacenter_name]))

    datacenter_svc = Datacenter(stub_config)
    datacenter_summaries = datacenter_svc.list(filter_spec)
    if len(datacenter_summaries) > 0:
        datacenter = datacenter_summaries[0].datacenter
        return datacenter
    else:
        return None
