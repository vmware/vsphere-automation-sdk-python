"""
* *******************************************************
* Copyright VMware, Inc. 2016-2018. All Rights Reserved.
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

from com.vmware.content_client import (Library,
                                       LocalLibrary,
                                       SubscribedLibrary)
from com.vmware.content.library_client import Item, SubscribedItem
from com.vmware.content.library.item_client import DownloadSession
from com.vmware.content.library.item_client import UpdateSession
from com.vmware.content.library.item.downloadsession_client import File as DownloadSessionFile
from com.vmware.content.library.item.updatesession_client import File as UpdateSessionFile
from com.vmware.vcenter_client import VM
from com.vmware.vcenter.iso_client import Image
from com.vmware.vcenter.ovf_client import LibraryItem
from com.vmware.vcenter.vm_template_client import LibraryItems as VmtxLibraryItem


class ClsApiClient(object):
    """
    This is a simplified wrapper around the Content Library APIs.
    It is used to access services exposed by Content Library Service.

    """

    def __init__(self, service_manager):
        # Client for all the services on a management node.
        self.service_manager = service_manager

        # Returns the service which provides support for generic functionality
        # which can be applied equally to all types of libraries
        self.library_service = Library(self.service_manager.stub_config)

        # Returns the service for managing local libraries
        self.local_library_service = LocalLibrary(self.service_manager.stub_config)

        # Returns the service for managing subscribed libraries
        self.subscribed_library_service = SubscribedLibrary(self.service_manager.stub_config)

        # Returns the service for managing library items
        self.library_item_service = Item(self.service_manager.stub_config)

        # Returns the service for managing sessions to update or delete content
        self.upload_service = UpdateSession(self.service_manager.stub_config)

        # Returns the service for managing files within an update session
        self.upload_file_service = UpdateSessionFile(self.service_manager.stub_config)

        # Returns the service for managing sessions to download content
        self.download_service = DownloadSession(self.service_manager.stub_config)

        # Returns the service for managing files within a download session
        self.download_file_service = DownloadSessionFile(self.service_manager.stub_config)

        # Returns the service for deploying virtual machines from OVF library items
        self.ovf_lib_item_service = LibraryItem(self.service_manager.stub_config)

        # Returns the service for mount and unmount of an iso file on a VM
        self.iso_service = Image(self.service_manager.stub_config)

        # Returns the service for managing subscribed library items
        self.subscribed_item_service = SubscribedItem(self.service_manager.stub_config)

        # Returns the service for managing library items containing virtual
        # machine templates
        self.vmtx_service = VmtxLibraryItem(self.service_manager.stub_config)

        # Creates the service that communicates with virtual machines
        self.vm_service = VM(self.service_manager.stub_config)
        # TODO: Add the other CLS services, eg. storage, config, type
