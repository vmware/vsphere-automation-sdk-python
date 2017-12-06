#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2017. All Rights Reserved.
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
__copyright__ = 'Copyright 2017 VMware, Inc.  All rights reserved.'
__vcenter_version__ = '6.6.2+'

from com.vmware.vcenter.vm_template_client import (
    LibraryItems as VmtxLibraryItem)

from samples.vsphere.common.id_generator import rand
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.vcenter.helper.vm_helper import get_vm


class CreateVmTemplate(SampleBase):
    """
    Demonstrates how to create a library item containing a native VMware
    virtual machine template from a virtual machine.

    Prerequisites:
        - A virtual machine
        - A datastore
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.vm_name = None
        self.datastore_name = None
        self.library_name = 'demo-vmtx-lib'
        self.item_name = None
        self.item_id = None

    def _options(self):
        self.argparser.add_argument('-vmname', '--vmname',
                                    required=True,
                                    help='The name of the source VM from '
                                         'which to create a library item')
        self.argparser.add_argument('-datastorename', '--datastorename',
                                    required=True,
                                    help='The name of the datastore in which '
                                         'to create a library and native VM '
                                         'template')
        self.argparser.add_argument('-itemname', '--itemname',
                                    help='The name of the library item to '
                                         'create. The item will contain a '
                                         'native VM template.')

    def _setup(self):
        # Required arguments
        self.vm_name = self.args.vmname
        self.datastore_name = self.args.datastorename

        # Optional arguments
        self.item_name = (self.args.itemname if self.args.itemname
                          else rand('vmtx-item-'))

        self.servicemanager = self.get_service_manager()
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        # Get the identifier of the source VM
        vm_id = get_vm(self.servicemanager.stub_config, self.vm_name)
        assert vm_id

        # Create a library
        storage_backings = self.helper.create_storage_backings(
            self.servicemanager, self.datastore_name)
        self.library_id = self.helper.create_local_library(storage_backings,
                                                           self.library_name)

        # Build the create specification
        create_spec = VmtxLibraryItem.CreateSpec()
        create_spec.source_vm = vm_id
        create_spec.library = self.library_id
        create_spec.name = self.item_name

        # Create a new library item from the source VM
        self.item_id = self.client.vmtx_service.create(create_spec)
        print("Created VM template item '{0}' with ID: {1}".format(
            self.item_name, self.item_id))

        # Retrieve the library item info
        info = self.client.vmtx_service.get(self.item_id)
        print('VM template guest OS: {0}'.format(info.guest_os))

    def _cleanup(self):
        if self.library_id:
            self.client.local_library_service.delete(self.library_id)
            print('Deleted library ID: {0}'.format(self.library_id))


def main():
    sample = CreateVmTemplate()
    sample.main()


if __name__ == '__main__':
    main()
