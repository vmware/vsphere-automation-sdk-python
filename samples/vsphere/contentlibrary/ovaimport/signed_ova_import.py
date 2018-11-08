#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2018. All Rights Reserved.
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
__copyright__ = 'Copyright 2018 VMware, Inc.  All rights reserved.'
__vcenter_version__ = '6.7u1+'

import time
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.content.library.item_client import UpdateSessionModel
from com.vmware.content.library.item.updatesession_client import (
    File as UpdateSessionFile, PreviewInfo, WarningType, WarningBehavior)
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper

AVAILABLE = PreviewInfo.State.AVAILABLE
NOT_APPLICABLE = PreviewInfo.State.NOT_APPLICABLE


class SignedOvaImport(SampleBase):
    """
    Demonstrates the workflow to import an OVA file into the content library,
    as an OVF library item.

    Note: the workflow needs an existing VC DS with available storage.
    """

    SIGNED_OVA_FILENAME = 'nostalgia-signed.ova'
    SIGNED_OVA_RELATIVE_DIR = '../resources/signedOvaWithCertWarning'

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.datastore_name = None
        self.lib_name = 'ova-demo-lib'
        self.local_lib_id = None
        self.lib_item_name = 'signedOvaImport'
        self.lib_item_id = None

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    required=True,
                                    help='The name of the datastore.')

    def _setup(self):
        self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        # Build the storage backing for the library to be created using given datastore name
        self.datastore_name = self.args.datastorename
        storage_backings = self.helper.create_storage_backings(service_manager=self.servicemanager,
                                                               datastore_name=self.datastore_name)

        # Create a local content library backed by the VC datastore using vAPIs
        self.local_lib_id = self.helper.create_local_library(storage_backings, self.lib_name)

        # Create a new library item in the content library for uploading the files
        self.lib_item_id = self.helper.create_library_item(library_id=self.local_lib_id,
                                                           item_name=self.lib_item_name,
                                                           item_description='Sample template from ova file',
                                                           item_type='ovf')
        print('Library item created. ID: {0}'.format(self.lib_item_id))

        ova_file_map = self.helper.get_ova_file_map(self.SIGNED_OVA_RELATIVE_DIR,
                                                    local_filename=self.SIGNED_OVA_FILENAME)
        # Create a new upload session for uploading the files
        # To ignore expected warnings and skip preview info check,
        # you can set create_spec.warning_behavior during session creation
        session_id = self.client.upload_service.create(
            create_spec=UpdateSessionModel(library_item_id=self.lib_item_id),
            client_token=generate_random_uuid())
        self.helper.upload_files_in_session(ova_file_map, session_id)

        # Wait for terminal preview state and obtain preview warnings if any
        self.wait_for_terminal_preview_state(session_id, AVAILABLE)
        session = self.client.upload_service.get(session_id)
        preview_info = session.preview_info

        # Collect generated preview warning types
        preview_warning_types = []
        print('Preview warnings for the session are the following:')
        for preview_warning in preview_info.warnings:
            print(preview_warning.message.default_message)
            preview_warning_types.append(preview_warning.type)

        # Ignore preview warnings on session
        ignore_warning_behaviors = []
        for warning_type in preview_warning_types:
            warning_behavior = WarningBehavior(type=warning_type, ignored=True)
            ignore_warning_behaviors.append(warning_behavior)
        self.client.upload_service.update(session_id, update_spec=UpdateSessionModel(
            warning_behavior=ignore_warning_behaviors))
        print('All preview warnings are ignored, proceeding to complete the session')

        self.client.upload_service.complete(session_id)
        self.client.upload_service.delete(session_id)
        print('Uploaded ova file as an ovf template to library item {0}'.format(self.lib_item_id))

    def wait_for_terminal_preview_state(self, session_id, expected_terminal_preview_state,
                                        timeout_sec=300):
        """
        Periodically checks update session for preview state to reach a terminal state.

        :param session_id: ID of update session for which preview state is checked
        :param expected_terminal_preview_state: expected terminal preview state
        :param timeout_sec: number of seconds to wait before timing out
        """
        preview_state = None
        start_time = time.time()
        terminal_preview_state_list = [NOT_APPLICABLE, AVAILABLE]
        while (time.time() - start_time) < timeout_sec:
            session = self.client.upload_service.get(session_id)
            if session.state == 'ERROR':
                raise Exception('Session is in error state, error message: {}'.format(
                    session.error_message))
            preview_state = session.preview_info.state
            # check if preview state is in one of the terminal states
            if preview_state not in terminal_preview_state_list:
                time.sleep(1)
            else:
                break

        if preview_state != expected_terminal_preview_state:
            raise Exception('Preview state did not reach expected {} state, actual preview state: '
                            '{}'.format(expected_terminal_preview_state, preview_state))

    def _cleanup(self):
        if self.local_lib_id:
            self.client.local_library_service.delete(library_id=self.local_lib_id)
            print('Deleted library ID: {0}'.format(self.local_lib_id))


def main():
    sample = SignedOvaImport()
    sample.main()


if __name__ == '__main__':
    main()
