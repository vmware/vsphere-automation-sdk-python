#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
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

from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper

from samples.vsphere.vcenter.helper.vm_helper import get_vm


class IsoMount(SampleBase):
    """
    Demonstrates the content library ISO item mount and
    unmount workflow via the mount and unmount APIs from the
    ISO service.
    """

    ISO_FILENAME = 'test.iso'

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.datastore_name = None
        self.lib_name = "iso-demo-lib"
        self.local_library = None
        self.iso_item_name = "iso-demo-lib-item"
        self.vm_name = None

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    help='The name of a datastore (of type vmfs) that is'
                                         ' acceassible to the vm specified with --vmname.')
        self.argparser.add_argument('-vmname',
                                    '--vmname',
                                    help='The name of the vm where iso will be mounted. '
                                         'The vm needs to be already created on the vCenter')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        self.vm_name = self.args.vmname
        assert self.vm_name is not None

        self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        storage_backings = self.helper.create_storage_backings(
            self.servicemanager, self.datastore_name)

        library_id = self.helper.create_local_library(storage_backings,
                                                      self.lib_name)
        self.local_library = self.client.local_library_service.get(library_id)

        library_item_id = self.helper.create_iso_library_item(library_id,
                                                              self.iso_item_name,
                                                              self.ISO_FILENAME)

        vm_id = get_vm(self.servicemanager.stub_config, self.vm_name)
        assert vm_id is not None

        # Mount the iso item as a CDROM device
        device_id = self.client.iso_service.mount(library_item_id, vm_id)
        assert device_id is not None
        print('Mounted library item {0} on vm {1} at device {2}'.
              format(self.iso_item_name, self.vm_name, device_id))
        # Unmount the CDROM
        self.client.iso_service.unmount(vm_id, device_id)
        print('Unmounted library item {0} from vm {1} mounted at device {2}'.
              format(self.iso_item_name, self.vm_name, device_id))

    def _cleanup(self):
        if self.local_library:
            self.client.local_library_service.delete(
                library_id=self.local_library.id)
            print('Deleted Library Id: {0}'.format(self.local_library.id))


def main():
    iso_mount_sample = IsoMount()
    iso_mount_sample.main()


if __name__ == '__main__':
    main()
