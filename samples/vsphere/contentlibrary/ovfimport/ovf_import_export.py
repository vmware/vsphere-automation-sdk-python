#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2016 VMware, Inc.  All rights reserved.'
__vcenter_version__ = '6.0+'

import tempfile
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.content_client import LibraryModel
from com.vmware.content.library_client import StorageBacking
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.common.vim.helpers.get_datastore_by_name import get_datastore_id


class OvfImportExport(SampleBase):
    """
    Demonstrates the workflow to import an OVF package into the content library,
    as well as download of an OVF template from the content library.

    Note: the workflow needs an existing VC DS with available storage.
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.datastore_name = None
        self.lib_name = "demo-lib"
        self.local_library = None
        self.lib_item_name = "simpleVmTemplate"
        self.library_item = None

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    help='The name of the datastore.')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        if not self.servicemanager:
            self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        # Find the datastore by the given datastore name using property collector
        self.datastore_id = get_datastore_id(service_manager=self.servicemanager, datastore_name=self.datastore_name)
        assert self.datastore_id is not None
        print('DataStore: {0} ID: {1}'.format(self.datastore_name, self.datastore_id))

        # Build the storage backing for the library to be created
        storage_backings = []
        storage_backing = StorageBacking(type=StorageBacking.Type.DATASTORE, datastore_id=self.datastore_id)
        storage_backings.append(storage_backing)

        # Build the specification for the library to be created
        create_spec = LibraryModel()
        create_spec.name = self.lib_name
        create_spec.description = "Local library backed by VC datastore"
        create_spec.type = create_spec.LibraryType.LOCAL
        create_spec.storage_backings = storage_backings

        # Create a local content library backed the VC datastore using vAPIs
        library_id = self.client.local_library_service.create(create_spec=create_spec,
                                                              client_token=generate_random_uuid())
        print('Local library created: ID: {0}'.format(library_id))
        self.local_library = self.client.local_library_service.get(library_id)

        # Create a new library item in the content library for uploading the files
        self.library_item_id = self.helper.create_library_item(library_id=self.local_library.id,
                                                               item_name=self.lib_item_name,
                                                               item_description='Sample simple VM template',
                                                               item_type='ovf')
        assert self.library_item_id is not None
        assert self.client.library_item_service.get(self.library_item_id) is not None
        print('Library item created id: {0}'.format(self.library_item_id))

        # Upload a VM template to the CL
        ovf_files_map = self.helper.get_ovf_files_map(ClsApiHelper.SIMPLE_OVF_RELATIVE_DIR)
        self.helper.upload_files(library_item_id=self.library_item_id, files_map=ovf_files_map)
        print('Uploaded ovf and vmdk files to library item {0}'.format(self.library_item_id))

        # Download the library item from the CL
        temp_dir = tempfile.mkdtemp(prefix='simpleVmTemplate-')
        print('Downloading library item {0} to directory {1}'.format(self.library_item_id, temp_dir))
        downloaded_files_map = self.helper.download_files(library_item_id=self.library_item_id, directory=temp_dir)
        assert len(downloaded_files_map) == len(ovf_files_map)

    def _cleanup(self):
        if self.local_library:
            self.client.local_library_service.delete(library_id=self.local_library.id)
            print('Deleted Library Id: {0}'.format(self.local_library.id))


def main():
    sample = OvfImportExport()
    sample.main()


if __name__ == '__main__':
    main()
