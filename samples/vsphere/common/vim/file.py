"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
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

import re

from samples.vsphere.common.vim.inventory import get_datastore_mo

from samples.vsphere.common.vim import datastore_file

datastore_path_regex = re.compile('\[(.+)\]\s?(.*)')


def parse_datastore_path(datastore_path):
    """Extract datastore name from datastore path"""
    m = datastore_path_regex.match(datastore_path)
    if m:
        (datastore_name, path) = m.groups()
        return datastore_name, path
    return None, None


def detect_directory(context, description, datacenter_name, datastore_path):
    """Find directory based on specific datacenter and datastore path"""
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        raise Exception("Could not find datastore '{}'".format(datastore_name))

    dsfile = datastore_file.File(datastore_mo)
    f = dsfile.list(datastore_path)
    if len(f) == 0:
        print("Failed to detect {} directory '{}'".format(description,
                                                          datastore_path))
        return False
    if f.type != datastore_file.FOLDER:
        print("Path '{}' is not a directory".format(datastore_path))
        return False
    return True


def create_directory(context, description, datacenter_name, datastore_path):
    """Create directory in specific datacenter"""
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        raise Exception("Could not find datastore '{}'".format(datastore_name))

    dsfile = datastore_file.File(datastore_mo)
    if not dsfile.exists(datastore_path):
        print("Creating {} directory '{}'".format(description, datastore_path))
        dsfile.mkdir(path, parent=True)
    else:
        # TODO Need to check that this is actually a directory.
        print("{} directory '{}' exists.".format(description, datastore_path))


def delete_directory(context, description, datacenter_name, datastore_path):
    """Delete directory from specific datacenter"""
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        return

    dsfile = datastore_file.File(datastore_mo)
    if dsfile.exists(datastore_path):
        print("Deleting {} directory '{}'.".format(description, datastore_path))
        dsfile.delete2(path)


def detect_file(context, description, datacenter_name, datastore_path):
    """Find specific file in specific datacenter"""
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        raise Exception("Could not find datastore '{}'".format(datastore_name))

    dsfile = datastore_file.File(datastore_mo)
    f = dsfile.list(datastore_path)
    if len(f) == 0:
        print("Failed to detect {} file '{}'".
              format(description, datastore_path))
        return False
    if f.type != datastore_file.FILE:
        print("Path '{}' is not a file".format(datastore_path))
        return False
    return True


def delete_file(client, service_instance,
                description, datacenter_name, datastore_path):
    """Delete a file from specific datacenter"""
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(client,
                                    service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        return

    dsfile = datastore_file.File(datastore_mo)
    if dsfile.exists(datastore_path):
        print("Deleting {} file '{}'.".format(description, datastore_path))
        dsfile.delete(path)
