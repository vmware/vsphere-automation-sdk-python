#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2019. All Rights Reserved.
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
__vcenter_version__ = '7.0.0+'

from pyVmomi import vim
from com.vmware.vcenter.vm_template.library_items_client import CheckOuts
from com.vmware.vcenter.vm_template.library_items_client import Versions

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.id_generator import rand
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common.vim.helpers.vim_utils import get_obj_by_moId
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.vcenter.helper.resource_pool_helper import (
    get_resource_pool)


class CheckOutVmTemplateWorkflow(SampleBase):
    """
    Demonstrates how to check out a VM from a library item containing a virtual
    machine template, check in the VM checked out from the item, and rollback
    the item to a previous version.

    Prerequisites:
        - A library item containing a virtual machine template
        - A resource pool
        - A datacenter
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.item_name = None
        self.vm_name = None
        self.datacenter_name = None
        self.resource_pool_name = None

    def _options(self):
        self.argparser.add_argument('-itemname', '--itemname',
                                    required=True,
                                    help='The name of the library item '
                                         'containing the VM template '
                                         'to be checked out')
        self.argparser.add_argument('-datacentername', '--datacentername',
                                    required=True,
                                    help='The name of the datacenter in which '
                                         'to check out the VM')
        self.argparser.add_argument('-resourcepoolname', '--resourcepoolname',
                                    required=True,
                                    help='The name of the resource pool in '
                                         'the datacenter in which to place '
                                         'the VM')
        self.argparser.add_argument('-vmname', '--vmname',
                                    help='The name of the VM to check out of '
                                         'the library item')

    def _setup(self):
        # Required arguments
        self.datacenter_name = self.args.datacentername
        self.resource_pool_name = self.args.resourcepoolname
        self.item_name = self.args.itemname

        # Optional arguments
        self.vm_name = (self.args.vmname if self.args.vmname
                        else rand('checked-out-vm-'))

        self.servicemanager = self.get_service_manager()
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

        session = get_unverified_session() if self.skip_verification else None
        self.vsphere_client = create_vsphere_client(server=self.server,
                                                    username=self.username,
                                                    password=self.password,
                                                    session=session)

    def _execute(self):
        # Get the identifiers
        item_id = self.helper.get_item_id_by_name(self.item_name)
        assert item_id

        resource_pool_id = get_resource_pool(self.vsphere_client,
                                             self.datacenter_name,
                                             self.resource_pool_name)
        assert resource_pool_id

        version_before_check_out = self.client.library_item_service.get(
            item_id).content_version

        self.print_live_versions(item_id)

        # Build the check out spec
        check_out_spec = CheckOuts.CheckOutSpec()
        placement_spec = CheckOuts.PlacementSpec()
        placement_spec.resource_pool = resource_pool_id
        check_out_spec.placement = placement_spec
        check_out_spec.name = self.vm_name

        # Check out VM from item
        vm_id = self.client.check_outs_service.check_out(item_id,
                                                         check_out_spec)
        print("VM (ID: {}) checked out from item".format(vm_id))

        # Get library id associated with checked out VM
        info = self.vsphere_client.vcenter.vm.LibraryItem.get(
            vm_id)
        assert info.check_out
        print("Library item associated with checked out VM is {}".format(
            info.check_out.library_item))

        # Check in VM into the library item
        check_in_spec = CheckOuts.CheckInSpec()
        check_in_spec.message = "Check in message"
        version_after_check_in = self.client.check_outs_service.check_in(
            item_id, vm_id, check_in_spec)
        print("VM (ID: {}) checked into item {}".format(vm_id, item_id))
        self.print_live_versions(item_id)

        # Rollback to previous version
        rollback_message = "Rollback to v{}".format(version_before_check_out)
        rollback_spec = Versions.RollbackSpec(rollback_message)
        version_after_rollback = self.client.versions_service.rollback(
            item_id, version_before_check_out, rollback_spec)
        print("Item rolled back to version {}. New item version is {}".format(
            version_before_check_out, version_after_rollback))
        self.print_live_versions(item_id)

        # Delete previous version
        self.client.versions_service.delete(item_id, version_after_check_in)
        print("Deleted version {} of item".format(version_after_check_in))
        self.print_live_versions(item_id)
        self.print_change_history(item_id)

    def print_live_versions(self, item_id):
        # Get and print live versions of the VM template item
        versions_info = self.client.versions_service.list(item_id)
        print("Live versions of VM template item:")
        for version_info in versions_info:
            vm_template = get_obj_by_moId(self.servicemanager.content,
                                          [vim.VirtualMachine],
                                          version_info.vm_template)
            print("Version: {}, VM template name: {}".format(
                version_info.version, vm_template.name))

    def print_change_history(self, item_id):
        # Get and print change history of the VM template item
        changes_summary = self.client.changes_service.list(item_id)
        print("Change history of VM template item:")
        for change_summary in changes_summary:
            print("Change version: {}, Time: {}, User: {}, Message: {}".format(
                change_summary.version, change_summary.time,
                change_summary.user, change_summary.short_message))


def main():
    check_out_workflow_sample = CheckOutVmTemplateWorkflow()
    check_out_workflow_sample.main()


if __name__ == '__main__':
    main()
