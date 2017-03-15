"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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

import pyVim.task
import requests
from pyVmomi import vim

from samples.vsphere.common.vim.inventory import get_datacenter_for_datastore

# TODO:
# verify=False in all cases.  Expose this as a top level control

debug = False

(FILE, FOLDER) = range(2)


class FileArray(list):
    def list(self, path=None):
        children = FileArray()
        for e in self:
            children += e.list(path)
        return children

    def __repr__(self):
        return '\n'.join([str(e) for e in self])

    def _check_unique(self):
        if len(self) == 0:
            raise Exception('FileArray: No elements')
        elif len(self) > 1:
            raise Exception('FileArray: Maybe applied to only one element')

    @property
    def path(self):
        self._check_unique()
        return self[0].path

    @property
    def datastore_path(self):
        self._check_unique()
        return self[0].datastore_path

    @property
    def datastore_mo(self):
        self._check_unique()
        return self[0].datastore_mo

    @property
    def type(self):
        self._check_unique()
        return self[0].type

    def list(self, path=None):
        self._check_unique()
        return self[0].list(path)

    def put(self, path=None, src_url=None, src_file=None, src_path=None,
            content=None):
        self._check_unique()
        return self[0].put(path, src_url, src_file, src_path, content)

    def get(self, path=None):
        self._check_unique()
        return self[0].get(path)

    def exists(self, path=None):
        self._check_unique()
        return self[0].exists(path)

    def delete(self, path=None):
        self._check_unique()
        return self[0].delete(path)

    def delete2(self, path=None):
        self._check_unique()
        return self[0].delete2(path)

    def mkdir(self, path=None, parent=None):
        self._check_unique()
        return self[0].mkdir(path, parent)


class File(object):
    """
    Utility class contains datastore related helper methods using vim API
    and HTTP requests module.
    """
    def __init__(self, parent=None, path=None, ftype=None):
        self._file_manager = None
        if isinstance(parent, vim.Datastore):
            # Iteratively look for the Datacenter parent
            self._datacenter_mo = get_datacenter_for_datastore(parent)
            self._datastore_mo = parent
            self._ftype = FOLDER
            if path:
                self._path = path
            else:
                self._path = ''
        elif isinstance(parent, File):
            self._datacenter_mo = parent._datacenter_mo
            self._datastore_mo = parent.datastore_mo
            self._ftype = ftype
            if parent._path == '':
                self._path = path
            else:
                self._path = '{}/{}'.format(parent._path, path)
        else:
            raise Exception(
                "Invalid type '{}' for datastore_file".format(type(parent)))

    def _get_file_manager(self):
        if not self._file_manager:
            soap_stub = self._datacenter_mo._stub
            service_instance = vim.ServiceInstance('ServiceInstance', soap_stub)
            self._file_manager = service_instance.content.fileManager
        return self._file_manager

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def get_datastore_path(self, path=None):
        if not path:
            return self.datastore_path

        paths = [p for p in [self._path, path] if p]
        return '[{}] {}'.format(self._datastore_mo.name, '/'.join(paths))

    @property
    def datastore_path(self):
        if self._path != '':
            return '[{}] {}'.format(self._datastore_mo.name, self._path)
        else:
            return '[{}]'.format(self._datastore_mo.name)

    @property
    def datastore_mo(self):
        return self._datastore_mo

    @datastore_mo.setter
    def datastore_mo(self, value):
        self._datastore_mo = value

    @property
    def type(self):
        return self._ftype

    @type.setter
    def type(self, value):
        self._ftype = value

    def to_string(self):
        s = ''
        if self._ftype == FOLDER:
            s += 'D '
        else:
            s += 'F '
        s += self.datastore_path
        return s

    def __repr__(self):
        return self.to_string()

    def list(self, path=None):
        match_pattern = None
        dirname = None

        if path is not None:
            # Determine the dirname and the basename making sure only the
            # basename is passed in the match_pattern
            paths = path.split('/')
            if len(paths) == 1:
                dirname = paths[0]
            else:
                path = paths[-1]
                dirname = '/'.join(paths[0:-1])
            match_pattern = [path]

        browser = self._datastore_mo.browser
        search_spec = vim.host.DatastoreBrowser.SearchSpec(
            query=[vim.host.DatastoreBrowser.FolderQuery(),
                   vim.host.DatastoreBrowser.Query()],
            details=vim.host.DatastoreBrowser.FileInfo.Details(fileType=True),
            matchPattern=match_pattern,
            sortFoldersFirst=True)
        if debug:
            print("list: dirname='{}' search_spec='{}'".
                  format(dirname, search_spec))
        task = browser.Search(dirname, search_spec)
        pyVim.task.WaitForTask(task)

        children = FileArray()
        for f in task.info.result.file:
            ftype = FILE
            if isinstance(f, vim.host.DatastoreBrowser.FolderInfo):
                ftype = FOLDER
            if dirname:
                children.append(
                    File(self, path='/'.join([dirname, f.path]), ftype=ftype))
            else:
                children.append(File(self, path=f.path, ftype=ftype))
        return children

    def _make_cookie(self, stub):
        cookies = {}
        for c in stub.cookie.split(';'):
            e = c.strip().split('=')
            if len(e) > 1:
                cookies[e[0]] = e[1]
        return cookies

    def exists(self, path=None):
        try:
            return len(self.list(path)) > 0
        except vim.fault.FileNotFound:
            return False

    def put(self, path=None, src_url=None, src_file=None, src_path=None,
            content=None):
        datacenter_name = self._datacenter_mo.name
        datastore_name = self._datastore_mo.name
        stub = self._datastore_mo._stub
        cookie = self._make_cookie(stub)
        f = None
        if src_file is not None:
            f = src_file
        elif src_url is not None:
            f = requests.get(src_url, stream=True)
        elif src_path is not None:
            f = open(src_file, 'wb')
        elif content is None:
            raise Exception('No input provided for put')

        if f:
            data = f
        else:
            data = content

        paths = ['https://{0}/folder'.format(stub.host)]
        if self._path:
            paths.append(self._path)
        if path:
            paths.append(path)
        url = '/'.join(paths)
        if debug:
            print("put: url is '{}'".format(url))

        r = requests.put(url, params={'dcPath': datacenter_name,
                                      'dsName': datastore_name},
                         cookies=cookie, verify=False, data=data)

        if f:
            f.close()
            f = None

        if r.status_code < 200 or r.status_code >= 300:
            raise Exception('Put failed with status {}'.format(r.status_code),
                            r)

    def get(self, path=None):
        datacenter_name = self._datacenter_mo.name
        datastore_name = self._datastore_mo.name
        stub = self._datastore_mo._stub
        cookie = self._make_cookie(stub)

        paths = ['https://{0}/folder'.format(stub.host)]
        if self._path:
            paths.append(self._path)
        if path:
            paths.append(path)
        url = '/'.join(paths)
        if debug:
            print("get: url is '{}'".format(url))

        r = requests.get(url, params={'dcPath': datacenter_name,
                                      'dsName': datastore_name},
                         cookies=cookie, verify=False, stream=True)

        if r.status_code < 200 or r.status_code >= 300:
            raise Exception('Get failed with status {}'.format(r.status_code),
                            r)

        return r

    def delete(self, path=None):
        datacenter_name = self._datacenter_mo.name
        datastore_name = self._datastore_mo.name
        stub = self._datastore_mo._stub
        cookie = self._make_cookie(stub)

        paths = ['https://{0}/folder'.format(stub.host)]
        if self._path:
            paths.append(self._path)
        if path:
            paths.append(path)
        url = '/'.join(paths)
        if debug:
            print("delete: url is '{}'".format(url))

        r = requests.delete(url, params={'dcPath': datacenter_name,
                                         'dsName': datastore_name},
                            cookies=cookie, verify=False)

        if r.status_code < 200 or r.status_code >= 300:
            raise Exception(
                'Delete failed with status {}'.format(r.status_code), r)

    def delete2(self, path=None):
        datacenter_mo = self._datacenter_mo
        file_manager = self._get_file_manager()
        datastore_path = self.get_datastore_path(path)
        if debug:
            print("delete2: datastore_path is '{}'".format(datastore_path))

            # TODO 'FileType' is not public?
            # file_manager.Delete(self._datacenter_mo, datastore_path, 'File')

    def mkdir(self, path=None, parent=False):
        datacenter_mo = self._datacenter_mo
        file_manager = self._get_file_manager()
        datastore_path = self.get_datastore_path(path)
        if debug:
            print("mkdir: datastore_path is '{}'".format(datastore_path))

        file_manager.MakeDirectory(datastore_path, self._datacenter_mo, parent)
