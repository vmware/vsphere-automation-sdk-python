"""
* *******************************************************
* Copyright (c) VMware, Inc. 2014, 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2014, 2016 VMware, Inc. All rights reserved.'


import pyVmomi
from com.vmware.content_client import Library
from com.vmware.vcenter.inventory_client import Datastore
from samples.vsphere.vim.helpers.vim_utils import get_obj_by_moId
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.logging_context import LoggingContext

logger = LoggingContext.get_logger('samples.vsphere.inventory.find_cl_datastore')


class FindClDatastore(SampleBase):
    """
    Demonstrate inventory APIs for retrieving information about vCenter datastore and network objects.
    Step 1: Retrieve an existing content library from its name.
    Step 2: Find out the content library storage backing.
    Step 3: Find out the vCenter object from the storage ID using datastore inventory API.
    Note: This sample needs an existing content library on the server
    (Please refer to samples.vsphere.contentlibrary.library_crud for details on how to create a content library)
    """
    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.cl_name = None
        self.library_service = None
        self.inv_datastore_service = None

    def _options(self):
        self.argparser.add_argument('-clname', '--clname', help='The name of the content library.')

    def _setup(self):
        if self.cl_name is None:
            self.cl_name = self.args.clname
        assert self.cl_name is not None

        if self.servicemanager is None:
            self.servicemanager = self.get_service_manager()

        self.library_service = Library(self.servicemanager.stub_config)
        self.inv_datastore_service = Datastore(self.servicemanager.stub_config)

    def _execute(self):
        library_model = self.find_cl_by_name()
        assert library_model is not None
        logger.info('Found CL: {0} Id: {1}'.format(library_model.name, library_model.id))

        datastore_ids = []
        for storage_backing in library_model.storage_backings:
            logger.info('Storage backing datastore id: {0} storage uri:{1}'
                        .format(storage_backing.datastore_id, storage_backing.storage_uri))
            if storage_backing.datastore_id is not None:
                datastore_ids.append(storage_backing.datastore_id)

        self.datastore_vim_objs = []  # for testing only
        datastores = self.inv_datastore_service.find(datastore_ids)
        for moid, info in datastores.items():
            logger.info('Datastore moid: {0} type: {1}'.format(moid, info.type))
            vim_type = self.get_vim_type(info.type)
            datastore = get_obj_by_moId(self.servicemanager.content, [vim_type], moid)
            assert datastore is not None
            logger.info('Vim object retrieved for datastore: {0}'.format(datastore.name))
            self.datastore_vim_objs.append(datastore)  # for testing only

    def _cleanup(self):
        pass

    def find_cl_by_name(self):
        for library_id in self.library_service.list():
            library_model = self.library_service.get(library_id)
            if library_model.name == self.cl_name:
                return library_model
        return None

    def get_vim_type(self, t):
        """
        Returns the vim type
        raises KeyError: If the type is not found
        """
        return pyVmomi.VmomiSupport.GetWsdlType('urn:vim25', t)


def main():
    find_cl_datastore = FindClDatastore()
    find_cl_datastore.main()

# Start program
if __name__ == '__main__':
    main()