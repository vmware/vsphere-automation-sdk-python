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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.0+'

from com.vmware.content.library_client import StorageBacking
from com.vmware.content_client import LibraryModel

from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.vim.helpers.get_datastore_by_name import get_datastore_id
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient


class LibraryCrud(SampleBase):
    """
    Demonstrates the basic operations of a content library. The sample also
    demonstrates the interoperability of the VIM and vAPI.

    Note: the workflow needs an existing VC DS with available storage.

    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.datastore_name = None
        self.lib_name = "demo-local-lib"
        self.local_library = None

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    help='The name of the datastore.')

    def _setup(self):
        if not self.datastore_name:
            self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        if not self.servicemanager:
            self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)

    def _execute(self):
        # List of visible content libraries
        visible_cls = self.client.local_library_service.list()
        if len(visible_cls) > 0:
            for visible_cl in visible_cls:
                get_visible_cl = self.client.local_library_service.get(visible_cl)
                print('Visible content library: {0} with id: {1}'.format(get_visible_cl.name, visible_cl))

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

        # Retrieve the local content library
        self.local_library = self.client.local_library_service.get(library_id)
        print('Retrieved library: ID: {0}'.format(self.local_library.id))

        # Update the local content library
        update_spec = LibraryModel()
        update_spec.description = "new description"
        self.client.local_library_service.update(library_id, update_spec)
        print('Updated library description')

    def _cleanup(self):
        if self.local_library:
            self.client.local_library_service.delete(library_id=self.local_library.id)
            print('Deleted Library Id: {0}'.format(self.local_library.id))


def main():
    sample = LibraryCrud()
    sample.main()


if __name__ == '__main__':
    main()
