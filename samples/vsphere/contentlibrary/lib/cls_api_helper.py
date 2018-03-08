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

import os
import ssl
import time

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.content_client import LibraryModel
from com.vmware.content.library_client import (Item,
                                               ItemModel,
                                               StorageBacking)
from com.vmware.content.library.item_client import (DownloadSessionModel,
                                                    UpdateSessionModel)
from com.vmware.content.library.item.downloadsession_client import File as DownloadSessionFile
from com.vmware.content.library.item.updatesession_client import File as UpdateSessionFile
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.vim.helpers.get_datastore_by_name import get_datastore_id


class ClsApiHelper(object):
    """
    Helper class to perform commonly used operations using Content Library API.

    """

    ISO_FILE_RELATIVE_DIR = '../resources/isoImages/'
    PLAIN_OVF_RELATIVE_DIR = '../resources/plainVmTemplate'
    SIMPLE_OVF_RELATIVE_DIR = '../resources/simpleVmTemplate'

    def __init__(self, cls_api_client, skip_verification):
        self.client = cls_api_client
        self.skip_verification = skip_verification

    def get_ovf_files_map(self, ovf_location):
        """
        Get OVF template file paths to be used during uploads

        Note: This method returns OVF template paths for the template included
              in the SDK resources directory
        """

        ovf_files_map = {}
        ovf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                               ovf_location))
        for file_name in os.listdir(ovf_dir):
            if file_name.endswith('.ovf') or file_name.endswith('.vmdk'):
                ovf_files_map[file_name] = os.path.join(ovf_dir, file_name)
        return ovf_files_map

    def create_local_library(self, storage_backings, lib_name):
        """
        :param storage_backings: Storage for the library
        :param lib_name: Name of the library
        :return: id of the created library
        """
        create_spec = LibraryModel()
        create_spec.name = lib_name
        create_spec.description = "Local library backed by VC datastore"
        create_spec.type = LibraryModel.LibraryType.LOCAL
        create_spec.storage_backings = storage_backings

        # Create a local content library backed the VC datastore
        library_id = self.client.local_library_service.create(create_spec=create_spec,
                                                              client_token=generate_random_uuid())
        print('Local library created, ID: {0}'.format(library_id))

        return library_id

    def create_storage_backings(self, service_manager, datastore_name):
        """
        :param service_manager:
        :param datastore_name: name of the datastore providing storage
        :return: the storage backing array
        """

        # Find the datastore by the given datastore name
        datastore_id = get_datastore_id(service_manager=service_manager,
                                        datastore_name=datastore_name)
        assert datastore_id is not None

        # If provided datastore is not of type vmfs, substitute the type
        # StorageBacking.Type.DATASTORE with StorageBacking.Type.OTHER
        # Build the specification for the library to be created
        storage_backings = [StorageBacking(type=StorageBacking.Type.DATASTORE,
                                           datastore_id=datastore_id)]
        return storage_backings

    def create_iso_library_item(self, library_id, iso_item_name, iso_filename):
        """
        :param library_id: item will be created on this library
        :param iso_item_name: name of the iso item to be created
        :param iso_filename: name of the iso file to be uploaded
        :return: id of the item created
        """
        # Create a new library item in the content library for uploading the files
        library_item_id = self.create_library_item(library_id=library_id,
                                                   item_name=iso_item_name,
                                                   item_description='Sample iso file',
                                                   item_type='iso')
        assert library_item_id is not None
        print('Library item created id: {0}'.format(library_item_id))

        # Upload an iso file to above library item, use the filename as the item_filename
        iso_files_map = self.get_iso_file_map(item_filename=iso_filename, disk_filename=iso_filename)
        self.upload_files(library_item_id=library_item_id, files_map=iso_files_map)
        print('Uploaded iso file to library item {0}'.format(library_item_id))
        return library_item_id

    def get_iso_file_map(self, item_filename, disk_filename):
        iso_files_map = {}
        iso_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     self.ISO_FILE_RELATIVE_DIR + disk_filename))
        iso_files_map[item_filename] = iso_file_path
        return iso_files_map

    def get_libraryitem_spec(self, client_token, name, description, library_id, library_item_type):
        """
        Create library item spec

        """
        lib_item_spec = ItemModel()
        lib_item_spec.name = name
        lib_item_spec.description = description
        lib_item_spec.library_id = library_id
        lib_item_spec.type = library_item_type
        return lib_item_spec

    def create_library_item(self, library_id, item_name, item_description, item_type):
        """
        Create a library item in the specified library

        """
        lib_item_spec = self.get_libraryitem_spec(client_token=generate_random_uuid(),
                                                  name=item_name,
                                                  description=item_description,
                                                  library_id=library_id,
                                                  library_item_type=item_type)
        # Create a library item
        return self.client.library_item_service.create(create_spec=lib_item_spec,
                                                       client_token=generate_random_uuid())

    def upload_files(self, library_item_id, files_map):
        """
        Upload a VM template to the published CL

        """
        # Create a new upload session for uploading the files
        session_id = self.client.upload_service.create(
            create_spec=UpdateSessionModel(library_item_id=library_item_id),
            client_token=generate_random_uuid())
        self.upload_files_in_session(files_map, session_id)
        self.client.upload_service.complete(session_id)
        self.client.upload_service.delete(session_id)

    def upload_files_in_session(self, files_map, session_id):
        for f_name, f_path in files_map.items():
            file_spec = self.client.upload_file_service.AddSpec(name=f_name,
                                                                source_type=UpdateSessionFile.SourceType.PUSH,
                                                                size=os.path.getsize(f_path))
            file_info = self.client.upload_file_service.add(session_id, file_spec)
            # Upload the file content to the file upload URL
            with open(f_path, 'rb') as local_file:
                request = urllib2.Request(file_info.upload_endpoint.uri, local_file)
                request.add_header('Cache-Control', 'no-cache')
                request.add_header('Content-Length', '{0}'.format(os.path.getsize(f_path)))
                request.add_header('Content-Type', 'text/ovf')
                if self.skip_verification and hasattr(ssl, '_create_unverified_context'):
                    # Python 2.7.9 has stronger SSL certificate validation,
                    # so we need to pass in a context when dealing with
                    # self-signed certificates.
                    context = ssl._create_unverified_context()
                    urllib2.urlopen(request, context=context)
                else:
                    # Don't pass context parameter since versions of Python
                    # before 2.7.9 don't support it.
                    urllib2.urlopen(request)

    def download_files(self, library_item_id, directory):
        """
        Download files from a library item

        Args:
            library_item_id: id for the library item to download files from
            directory: location on the client machine to download the files into

        """
        downloaded_files_map = {}
        # create a new download session for downloading the session files
        session_id = self.client.download_service.create(create_spec=DownloadSessionModel(
            library_item_id=library_item_id),
            client_token=generate_random_uuid())
        file_infos = self.client.download_file_service.list(session_id)
        for file_info in file_infos:
            self.client.download_file_service.prepare(session_id, file_info.name)
            download_info = self.wait_for_prepare(session_id, file_info.name)
            if self.skip_verification and hasattr(ssl, '_create_unverified_context'):
                # Python 2.7.9 has stronger SSL certificate validation,
                # so we need to pass in a context when dealing with self-signed
                # certificates.
                context = ssl._create_unverified_context()
                response = urllib2.urlopen(
                    url=download_info.download_endpoint.uri,
                    context=context)
            else:
                # Don't pass context parameter since versions of Python
                # before 2.7.9 don't support it.
                response = urllib2.urlopen(download_info.download_endpoint.uri)
            file_path = os.path.join(directory, file_info.name)
            with open(file_path, 'wb') as local_file:
                local_file.write(response.read())
            downloaded_files_map[file_info.name] = file_path
        self.client.download_service.delete(session_id)
        return downloaded_files_map

    def wait_for_prepare(self, session_id, file_name,
                         status_list=(DownloadSessionFile.PrepareStatus.PREPARED,),
                         timeout=30, sleep_interval=1):
        """
        Waits for a file to reach a status in the status list (default: prepared)
        This method will either timeout or return the result of
        downloadSessionFile.get(session_id, file_name)

        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            file_info = self.client.download_file_service.get(session_id, file_name)
            if file_info.status in status_list:
                return file_info
            else:
                time.sleep(sleep_interval)
        raise Exception(
            'timed out after waiting {0} seconds for file {1} to reach a terminal state'.format(
                timeout, file_name))

    def get_item_id_by_name(self, name):
        """
        Returns the identifier of the item with the given name.

        Args:
            name (str): The name of item to look for

        Returns:
            str: The item ID or None if the item is not found
        """
        find_spec = Item.FindSpec(name=name)
        item_ids = self.client.library_item_service.find(find_spec)
        item_id = item_ids[0] if item_ids else None
        if item_id:
            print('Library item ID: {0}'.format(item_id))
        else:
            print("Library item with name '{0}' not found".format(name))
        return item_id
