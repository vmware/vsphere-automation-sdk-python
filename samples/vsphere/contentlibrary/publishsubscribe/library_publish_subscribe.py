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

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.content_client import LibraryModel
from com.vmware.content.library_client import (ItemModel, PublishInfo,
                                               StorageBacking, SubscriptionInfo)
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.contentlibrary.lib.cls_sync_helper import ClsSyncHelper


class LibraryPublishSubscribe(SampleBase):
    """
    Demonstrates the basic sync workflow to publish and subscribe content libraries.
    Note: the workflow needs an existing VC datastore with available storage.
    """
    VCSP_USERNAME = 'vcsp'
    DEMO_PASSWORD = 'Password!23'
    SYNC_TIMEOUT_SEC = 60
    DEMO_FILENAME = 'test.iso'

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.datastore_name = None
        self.pub_lib_name = "demo-publib"
        self.sub_lib_name = "demo-sublib"
        self.pub_lib_id = None
        self.sub_lib_id = None

    def _options(self):
        self.argparser.add_argument('-datastorename',
                                    '--datastorename',
                                    help='The name of the datastore.')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None

        self.servicemanager = self.get_service_manager()
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        storage_backings = self.helper.create_storage_backings(
            self.servicemanager,
            self.datastore_name)

        # Create a published library backed the VC datastore using vAPIs
        self.pub_lib_id = self.create_published_library(storage_backings)
        assert self.pub_lib_id is not None
        print('Published library created: ID: {0}'.format(self.pub_lib_id))
        pub_lib = self.client.local_library_service.get(self.pub_lib_id)
        pub_lib_url = pub_lib.publish_info.publish_url
        assert pub_lib_url is not None
        print('Publish URL : {0}'.format(pub_lib_url))

        # Create a library item in the published library
        pub_lib_item_id = self.helper.create_iso_library_item(self.pub_lib_id,
                                                              'item_1',
                                                              self.DEMO_FILENAME)
        assert self.client.library_item_service.get(pub_lib_item_id) is not None

        # Create the subscribed library
        sub_lib, sub_spec = self.create_subcribed_library(storage_backings,
                                                          pub_lib_url)
        assert self.sub_lib_id is not None
        print('Subscribed library created: ID: {0}'.format(self.sub_lib_id))

        # It is not mandatory to verify sync, it is just for demonstrating the sample workflow.
        assert (ClsSyncHelper(self.client, self.SYNC_TIMEOUT_SEC).
                verify_library_sync(self.pub_lib_id, sub_lib))
        sub_lib = self.client.subscribed_library_service.get(self.sub_lib_id)
        print('Subscribed library synced : {0}'.format(sub_lib.last_sync_time))

        sub_item_ids = self.client.library_item_service.list(self.sub_lib_id)
        assert len(sub_item_ids) == 1, 'Subscribed library must have one item'

        # Add another item to the published library
        self.helper.create_iso_library_item(self.pub_lib_id, 'item_2',
                                            self.DEMO_FILENAME)

        # Manually synchronize the subscribed library to get the latest changes immediately.
        self.client.subscribed_library_service.sync(self.sub_lib_id)
        # It is not mandatory to verify sync, it is just for demonstrating the sample workflow.
        assert (ClsSyncHelper(self.client, self.SYNC_TIMEOUT_SEC).
                verify_library_sync(self.pub_lib_id, sub_lib))
        sub_lib = self.client.subscribed_library_service.get(self.sub_lib_id)
        print('Subscribed library synced : {0}'.format(sub_lib.last_sync_time))

        # List the subscribed items.
        sub_item_ids = self.client.library_item_service.list(self.sub_lib_id)
        assert len(sub_item_ids) == 2, 'Subscribed library must have two items'
        for sub_item_id in sub_item_ids:
            sub_item = self.client.library_item_service.get(sub_item_id)
            print('Subscribed item : {0}'.format(sub_item.name))

        # Change the subscribed library to be on-demand
        sub_spec.subscription_info.on_demand = True
        self.client.subscribed_library_service.update(self.sub_lib_id, sub_spec)

        # Evict the cached content of the first subscribed library item
        self.client.subscribed_item_service.evict(sub_item_id)
        sub_item = self.client.library_item_service.get(sub_item_id)
        print('Subscribed item evicted : {0}'.format(sub_item.name))
        assert not sub_item.cached, 'Subscribed item must not be cached'

        # Force synchronize the subscribed library item to fetch and cache the content
        self.client.subscribed_item_service.sync(sub_item_id, True)
        # It is not mandatory to verify sync, it is just for demonstrating the sample workflow.
        assert (ClsSyncHelper(self.client, self.SYNC_TIMEOUT_SEC).
                verify_item_sync(sub_item_id))
        sub_item = self.client.library_item_service.get(sub_item_id)
        print('Subscribed item force sync : {0}'.format(sub_item.name))
        assert sub_item.cached, 'Subscribed item must be cached'

    def create_published_library(self, storage_backings):
        # Build the authenticated publish info.
        # Note: The username will be 'vcsp'.
        pub_info = PublishInfo()
        pub_info.published = True
        pub_info.authentication_method = PublishInfo.AuthenticationMethod.BASIC
        pub_info.password = self.DEMO_PASSWORD

        # Build the specification for the published library to be created
        pub_spec = LibraryModel()
        pub_spec.name = self.pub_lib_name
        pub_spec.description = "Published library backed by VC datastore"
        pub_spec.publish_info = pub_info
        pub_spec.type = pub_spec.LibraryType.LOCAL
        pub_spec.storage_backings = storage_backings

        pub_lib_id = self.client.local_library_service.create(
            create_spec=pub_spec, client_token=generate_random_uuid())

        return pub_lib_id

    def create_subcribed_library(self, storage_backings, pub_lib_url):
        # Build the subscription information using the publish URL of the published
        # library. The username must be 'vcsp'.
        sub_info = SubscriptionInfo()
        sub_info.authentication_method = SubscriptionInfo.AuthenticationMethod.BASIC
        sub_info.user_name = self.VCSP_USERNAME
        sub_info.password = self.DEMO_PASSWORD
        sub_info.on_demand = False
        sub_info.automatic_sync_enabled = True
        sub_info.subscription_url = pub_lib_url

        # Build the specification for the subscribed library
        sub_spec = LibraryModel()
        sub_spec.name = self.sub_lib_name
        sub_spec.type = sub_spec.LibraryType.SUBSCRIBED
        sub_spec.subscription_info = sub_info
        sub_spec.storage_backings = storage_backings

        self.sub_lib_id = self.client.subscribed_library_service.create(
            create_spec=sub_spec, client_token=generate_random_uuid())
        sub_lib = self.client.subscribed_library_service.get(self.sub_lib_id)
        return sub_lib, sub_spec

    def _cleanup(self):
        if self.sub_lib_id:
            self.client.subscribed_library_service.delete(self.sub_lib_id)
            print('Deleted subscribed library Id: {0}'.format(self.sub_lib_id))

        if self.pub_lib_id:
            self.client.local_library_service.delete(self.pub_lib_id)
            print('Deleted published library Id : {0}'.format(self.pub_lib_id))


def main():
    sample = LibraryPublishSubscribe()
    sample.main()


if __name__ == '__main__':
    main()
