#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2016, 2018. All Rights Reserved.
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
__vcenter_version__ = '6.0+'

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
from com.vmware.vcenter.ovf_client import LibraryItem
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.vcenter.helper.vm_helper import get_vm


class CaptureVMTemplateToContentLibrary(SampleBase):
    """
    Demonstrates the workflow to capture a virtual machine into a content library.

    Note: The sample needs an existing virtual machine to capture.
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.datastore_name = None
        self.datastore_id = None
        self.cl_name = "LocalLibraryToCapture"
        self.vm_name = None
        self.vm_template_name = 'CapturedOvf'
        self.vm_template_description = 'Captured OVF description'
        self.deployable_resource_type = 'VirtualMachine'  # Substitute 'VirtualApp' for vApp

        self.content_library = None
        self.library_item_id = None

    def _options(self):
        self.argparser.add_argument('-datastorename', '--datastorename',
                                    required=True,
                                    help='The name of the datastore for'
                                         ' content library backing (of type vmfs)')
        self.argparser.add_argument('-vmname', '--vmname',
                                    required=True,
                                    help='Name of the VM to be captured')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        self.vm_name = self.args.vmname
        assert self.vm_name is not None

        if self.servicemanager is None:
            self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

        session = get_unverified_session() if self.skip_verification else None
        self.vsphere_client = create_vsphere_client(server=self.server,
                                                    username=self.username,
                                                    password=self.password,
                                                    session=session)

    def _execute(self):
        storage_backings = self.helper.create_storage_backings(
            self.servicemanager,
            self.datastore_name)

        print('Creating Content Library')
        # Create a content library
        library_id = self.helper.create_local_library(storage_backings,
                                                      self.cl_name)
        self.content_library = self.client.local_library_service.get(library_id)

        vm_id = get_vm(self.vsphere_client, self.vm_name)
        assert vm_id is not None

        param = self.create_capture_param(self.content_library,
                                          self.vm_template_name,
                                          self.vm_template_description)
        self.library_item_id = self.capture_source_vm(vm_id, param)
        assert self.library_item_id is not None
        assert self.client.library_item_service.get(self.library_item_id) is not None
        print('The VM id : {0} is captured as vm template library item id : {1}'.format
              (vm_id, self.library_item_id))

    def capture_source_vm(self, vm_id, param):
        source = LibraryItem.DeployableIdentity(self.deployable_resource_type,
                                                vm_id)
        result = self.client.ovf_lib_item_service.create(source,
                                                         param["target"],
                                                         param["spec"],
                                                         client_token=generate_random_uuid())
        return result.ovf_library_item_id

    def create_capture_param(self, library, name, description):
        spec = LibraryItem.CreateSpec(name=name,
                                      description=description)
        target = LibraryItem.CreateTarget(library_id=library.id,
                                          library_item_id=None)
        return {"target": target, "spec": spec}

    def _cleanup(self):
        # delete the local library.
        if self.content_library is not None:
            self.client.local_library_service.delete(
                library_id=self.content_library.id)
            print('Deleted Library Id: {0}'.format
                  (self.content_library.id))


def main():
    vm_template_capture = CaptureVMTemplateToContentLibrary()
    vm_template_capture.main()


# Start program
if __name__ == '__main__':
    main()
