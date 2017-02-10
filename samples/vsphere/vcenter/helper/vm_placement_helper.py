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

from com.vmware.vcenter_client import VM

from samples.vsphere.vcenter.helper import datastore_helper
from samples.vsphere.vcenter.helper import folder_helper
from samples.vsphere.vcenter.helper import resource_pool_helper


def get_placement_spec_for_resource_pool(stub_config,
                                         datacenter_name,
                                         vm_folder_name,
                                         datastore_name):
    """
    Returns a VM placement spec for a resourcepool. Ensures that the
    vm folder and datastore are all in the same datacenter which is specified.
    """
    resource_pool = resource_pool_helper.get_resource_pool(stub_config,
                                                           datacenter_name)

    folder = folder_helper.get_folder(stub_config,
                                      datacenter_name,
                                      vm_folder_name)

    datastore = datastore_helper.get_datastore(stub_config,
                                               datacenter_name,
                                               datastore_name)

    # Create the vm placement spec with the datastore, resource pool and vm
    # folder
    placement_spec = VM.PlacementSpec(folder=folder,
                                      resource_pool=resource_pool,
                                      datastore=datastore)

    print("get_placement_spec_for_resource_pool: Result is '{}'".
          format(placement_spec))
    return placement_spec
