#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2017-2018. All Rights Reserved.
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
__vcenter_version__ = '6.6.2+'

from pyVmomi import vim
from com.vmware.vcenter.vm_template_client import (
    LibraryItems as VmtxLibraryItem)

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.id_generator import rand
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common.vim.helpers.get_datastore_by_name import (
    get_datastore_id)
from samples.vsphere.common.vim.helpers.vim_utils import (
    delete_object, get_obj_by_moId)
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.vcenter.helper.folder_helper import get_folder
from samples.vsphere.vcenter.helper.resource_pool_helper import (
    get_resource_pool)


class DeployVmTemplate(SampleBase):
    """
    Demonstrates how to deploy a virtual machine from a library item containing
    a virtual machine template.

    Prerequisites:
        - A library item containing a virtual machine template
        - A datacenter
        - A VM folder
        - A resource pool
        - A datastore
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.item_name = None
        self.datacenter_name = None
        self.folder_name = None
        self.resource_pool_name = None
        self.datastore_name = None
        self.vm_name = None
        self.vm_id = None
        self.vm = None

    def _options(self):
        self.argparser.add_argument('-itemname', '--itemname',
                                    required=True,
                                    help='The name of the library item '
                                         'containing a VM template to be '
                                         'deployed')
        self.argparser.add_argument('-datacentername', '--datacentername',
                                    required=True,
                                    help='The name of the datacenter in which '
                                         'to deploy a VM')
        self.argparser.add_argument('-foldername', '--foldername',
                                    required=True,
                                    help='The name of the VM folder in the '
                                         'datacenter in which to place the '
                                         'deployed VM')
        self.argparser.add_argument('-resourcepoolname', '--resourcepoolname',
                                    required=True,
                                    help='The name of the resource pool in '
                                         'the datacenter in which to place '
                                         'the deployed VM')
        self.argparser.add_argument('-datastorename', '--datastorename',
                                    required=True,
                                    help='The name of the datastore to store '
                                         'the deployed VM home and disks')
        self.argparser.add_argument('-vmname', '--vmname',
                                    help='The name of the deployed VM')

    def _setup(self):
        # Required arguments
        self.item_name = self.args.itemname
        self.datacenter_name = self.args.datacentername
        self.folder_name = self.args.foldername
        self.resource_pool_name = self.args.resourcepoolname
        self.datastore_name = self.args.datastorename

        # Optional arguments
        self.vm_name = self.args.vmname if self.args.vmname else rand('vm-')

        self.servicemanager = self.get_service_manager()
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

        session = get_unverified_session() if self.skip_verification else None
        self.vsphere_client = create_vsphere_client(server=self.server,
                                                    username=self.username,
                                                    password=self.password,
                                                    session=session)

    def _execute(self):
        # Get the identifiers of the resources used for deployment
        item_id = self.helper.get_item_id_by_name(self.item_name)
        assert item_id
        folder_id = get_folder(self.vsphere_client,
                               self.datacenter_name,
                               self.folder_name)
        assert folder_id
        resource_pool_id = get_resource_pool(self.vsphere_client,
                                             self.datacenter_name,
                                             self.resource_pool_name)
        assert resource_pool_id
        datastore_id = get_datastore_id(self.servicemanager,
                                        self.datastore_name)
        assert datastore_id

        # Build the deployment specification
        placement_spec = VmtxLibraryItem.DeployPlacementSpec(
            folder=folder_id,
            resource_pool=resource_pool_id)
        vm_home_storage_spec = VmtxLibraryItem.DeploySpecVmHomeStorage(
            datastore=datastore_id)
        disk_storage_spec = VmtxLibraryItem.DeploySpecDiskStorage(
            datastore=datastore_id)
        deploy_spec = VmtxLibraryItem.DeploySpec(
            name=self.vm_name,
            placement=placement_spec,
            vm_home_storage=vm_home_storage_spec,
            disk_storage=disk_storage_spec)

        # Deploy a virtual machine from the VM template item
        self.vm_id = self.client.vmtx_service.deploy(item_id, deploy_spec)
        self.vm = get_obj_by_moId(self.servicemanager.content,
                                  [vim.VirtualMachine], self.vm_id)
        print("Deployed VM '{0}' with ID: {1}".format(self.vm.name,
                                                      self.vm_id))

        # Print a summary of the deployed VM
        vm_summary = self.vm.summary.config
        print('Guest OS: {0}'.format(vm_summary.guestId))
        print('{0} CPU(s)'.format(vm_summary.numCpu))
        print('{0} MB memory'.format(vm_summary.memorySizeMB))
        print('{0} disk(s)'.format(vm_summary.numVirtualDisks))
        print('{0} network adapter(s)'.format(vm_summary.numEthernetCards))

    def _cleanup(self):
        if self.vm:
            delete_object(self.servicemanager.content, self.vm)


def main():
    sample = DeployVmTemplate()
    sample.main()


if __name__ == '__main__':
    main()
