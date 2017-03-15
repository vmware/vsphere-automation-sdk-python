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

import time


class ClsSyncHelper:
    """
    Helper class to wait for the subscribed libraries and items to be
    synchronized completely with the publisher.
    """
    wait_interval_sec = 1
    start_time = None
    sync_timeout_sec = None

    def __init__(self, cls_api_client, sync_timeout_sec):
        self.client = cls_api_client
        self.sync_timeout_sec = sync_timeout_sec

    def verify_library_sync(self, pub_lib_id, sub_lib):
        """
        Wait until the subscribed library and its items are synchronized with
        the published library.
        """
        self.start_time = time.time()
        if not self.verify_same_items(pub_lib_id, sub_lib.id):
            return False

        sub_item_ids = self.client.library_item_service.list(sub_lib.id)
        for sub_item_id in sub_item_ids:
            if not self.verify_item_sync(sub_item_id):
                return False

        if not self.verify_library_last_sync_time(sub_lib):
            return False

        return True

    def verify_item_sync(self, sub_item_id):
        """
        Wait until the subscribed item is synchronized with the published item.
        """
        self.start_time = time.time()
        is_synced = False
        pub_item_id = self.client.library_item_service.get(
            sub_item_id).source_id
        pub_item = self.client.library_item_service.get(pub_item_id)

        while self.not_timed_out():
            sub_item = self.client.library_item_service.get(sub_item_id)
            # Verify if the subscribed item is the latest
            if (sub_item.metadata_version == pub_item.metadata_version and
                        sub_item.content_version == pub_item.content_version):
                is_synced = True
                break
            time.sleep(self.wait_interval_sec)

        return is_synced

    def verify_same_items(self, pub_lib_id, sub_lib_id):
        """
        Wait until the subscribed library has the same source item IDs as the
        published library.
        """
        is_synced = False
        pub_item_ids = self.client.library_item_service.list(pub_lib_id)

        while self.not_timed_out():
            sub_item_ids = self.client.library_item_service.list(sub_lib_id)

            if self.has_same_items(pub_item_ids, sub_item_ids):
                is_synced = True
                break
            time.sleep(self.wait_interval_sec)

        return is_synced

    def verify_library_last_sync_time(self, sub_lib):
        """
        Wait until the subscribed library's last sync time is populated.
        """
        is_synced = False

        while self.not_timed_out():
            # Get the subscribed library's updated information from server.
            refreshed_sub_lib = self.client.subscribed_library_service.get(
                sub_lib.id)
            if refreshed_sub_lib.last_sync_time is not None:
                if (sub_lib.last_sync_time is None or
                            refreshed_sub_lib.last_sync_time > sub_lib.last_sync_time):
                    is_synced = True
                    break
            time.sleep(self.wait_interval_sec)

        return is_synced

    def has_same_items(self, pub_item_ids, sub_item_ids):
        """
        Check if the subscribed library contains the same items as the
        published library. The item versions are not checked.
        """
        if len(pub_item_ids) != len(sub_item_ids):
            return False
        synced_item_ids = []
        for sub_item_id in sub_item_ids:
            source_id = self.client.library_item_service.get(
                sub_item_id).source_id
            if source_id not in synced_item_ids and source_id in pub_item_ids:
                synced_item_ids.append(sub_item_id)

        return len(pub_item_ids) == len(synced_item_ids)

    def not_timed_out(self):
        """
        Check if sync is not timed out yet.
        """
        elasped_time = time.time() - self.start_time
        return elasped_time < self.sync_timeout_sec
