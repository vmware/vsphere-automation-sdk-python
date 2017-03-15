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

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.content.library.item_client import UpdateSessionModel
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper


class ContentUpdate(SampleBase):
    """
    Demonstrates the workflow of updating a content library item.

    Note: the workflow needs an existing datastore (of type vmfs) with available storage.
    """

    ISO_FILE_1 = 'test.iso'
    ISO_FILE_2 = 'test-2.iso'
    ISO_ITEM_NAME = 'test'

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.datastore_name = None
        self.lib_name = "demo-lib"
        self.local_library = None

    def _options(self):
        self.argparser.add_argument('-datastorename', '--datastorename',
                                    help='The name of the datastore where '
                                         'the library will be created.')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        self.servicemanager = self.get_service_manager()
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        storage_backings = self.helper.create_storage_backings(self.servicemanager,
                                                               self.datastore_name)

        library_id = self.helper.create_local_library(storage_backings, self.lib_name)
        self.local_library = self.client.local_library_service.get(library_id)
        self.delete_and_upload_scenario(library_id)
        self.replace_scenario(library_id)

    def replace_scenario(self, library_id):
        """
        :param library_id: the Iso item will be created, and then replaced in this library
        :return: None

        Content update scenario 2:
        Update ISO library item by creating an update session for the
        item, then adding the new ISO file using the same session file
        name into the update session, which will replace the existing
        ISO file upon session complete.
        """

        iso_item_id = self.helper.create_library_item(library_id=library_id,
                                                      item_name=self.ISO_ITEM_NAME,
                                                      item_description='Sample iso file',
                                                      item_type='iso')
        print('ISO Library item version (on creation) {0}:'.format(
            self.get_item_version(iso_item_id)))

        iso_files_map = self.helper.get_iso_file_map(item_filename=self.ISO_FILE_1,
                                                     disk_filename=self.ISO_FILE_1)
        self.helper.upload_files(library_item_id=iso_item_id, files_map=iso_files_map)
        original_version = self.get_item_version(iso_item_id)
        print('ISO Library item version (on original content upload) {0}:'.format(
            original_version))

        session_id = self.client.upload_service.create(
            create_spec=UpdateSessionModel(library_item_id=iso_item_id),
            client_token=generate_random_uuid())
        # Use the same item filename (update endpoint, as it's a replace scenario)
        iso_files_map = self.helper.get_iso_file_map(item_filename=self.ISO_FILE_1,
                                                     disk_filename=self.ISO_FILE_2)

        self.helper.upload_files_in_session(iso_files_map, session_id)
        self.client.upload_service.complete(session_id)
        self.client.upload_service.delete(session_id)
        updated_version = self.get_item_version(iso_item_id)
        print('ISO Library item version (after content update): {0}'.format(
            updated_version))
        assert updated_version > original_version, 'content update should increase the version'

    def delete_and_upload_scenario(self, library_id):
        """
        :param library_id: the OVF item will be created and updated in this library
        :return: None

        Content update scenario 1:
        Update OVF library item by creating an update session for the
        OVF item, removing all existing files in the session, then
        adding all new files into the same update session, and completing
        the session to finish the content update.
        """

        # Create a new library item in the content library for uploading the files
        ovf_item_id = self.helper.create_library_item(library_id=library_id,
                                                      item_name='demo-ovf-item',
                                                      item_description='Sample simple VM template',
                                                      item_type='ovf')
        assert ovf_item_id is not None
        print('Library item created id: {0}'.format(ovf_item_id))
        print('OVF Library item version (at creation) {0}:'.format(
            self.get_item_version(ovf_item_id)))

        # Upload a VM template to the CL
        ovf_files_map = self.helper.get_ovf_files_map(ClsApiHelper.SIMPLE_OVF_RELATIVE_DIR)
        self.helper.upload_files(library_item_id=ovf_item_id, files_map=ovf_files_map)
        print('Uploaded ovf and vmdk files to library item {0}'.format(ovf_item_id))
        original_version = self.get_item_version(ovf_item_id)
        print('OVF Library item version (on original content upload): {0}'.format(
            original_version))

        # Create a new session and perform content update
        session_id = self.client.upload_service.create(
            create_spec=UpdateSessionModel(library_item_id=ovf_item_id),
            client_token=generate_random_uuid())
        existing_files = self.client.upload_file_service.list(session_id)
        for file in existing_files:
            print('deleting {0}'.format(file.name))
            self.client.upload_file_service.remove(session_id, file.name)
        ovf_files_map = self.helper.get_ovf_files_map(
            ovf_location=ClsApiHelper.PLAIN_OVF_RELATIVE_DIR)
        self.helper.upload_files_in_session(ovf_files_map, session_id)
        self.client.upload_service.complete(session_id)
        self.client.upload_service.delete(session_id)
        updated_version = self.get_item_version(ovf_item_id)
        print('OVF Library item version (after content update): {0}'.format(
            updated_version))
        assert updated_version > original_version, 'content update should increase the version'

    def get_item_version(self, item_id):
        ovf_item_model = self.client.library_item_service.get(item_id)
        pre_update_version = ovf_item_model.content_version
        return pre_update_version

    def _cleanup(self):
        if self.local_library:
            self.client.local_library_service.delete(library_id=self.local_library.id)
            print('Deleted Library Id: {0}'.format(self.local_library.id))


def main():
    content_update_sample = ContentUpdate()
    content_update_sample.main()


if __name__ == '__main__':
    main()
