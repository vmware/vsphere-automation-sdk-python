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


from samples.vsphere.common.vim.file import (detect_file, delete_file,
                                             parse_datastore_path)
from samples.vsphere.common.vim.inventory import get_datastore_mo

from samples.vsphere.common.vim import datastore_file


def setup_iso_image(context):
    """Copy iso image used to run vcenter samples"""
    iso_src_url = context.testbed.config['ISO_SRC_URL']
    datacenter_name = context.testbed.config['ISO_DATACENTER_NAME']
    datastore_path = context.testbed.config['ISO_DATASTORE_PATH']
    (datastore_name, path) = parse_datastore_path(datastore_path)
    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        raise Exception("Could not find datastore '{}'".format(datastore_name))

    # See if the ISO image exists. Copy it into the system if it does not exist
    dsfile = datastore_file.File(datastore_mo)
    if not dsfile.exists(datastore_path):
        print("Putting ISO image file from '{}' at '{}'".
              format(iso_src_url, datastore_path))
        dsfile.put(path=path, src_url=iso_src_url)


def cleanup_iso_image(context):
    """Cleanup iso image after sample run"""
    datacenter_name = context.testbed.config['ISO_DATACENTER_NAME']
    datastore_path = context.testbed.config['ISO_DATASTORE_PATH']
    delete_file(context.client,
                context.service_instance,
                "ISO Image",
                datacenter_name,
                datastore_path)


def detect_iso_image(context):
    """Find iso image used to run vcenter samples"""
    datacenter_name = context.testbed.config['ISO_DATACENTER_NAME']
    datastore_path = context.testbed.config['ISO_DATASTORE_PATH']
    return detect_file(context, "ISO Image", datacenter_name, datastore_path)


def setup(context):
    setup_iso_image(context)


def cleanup(context):
    cleanup_iso_image(context)


def validate(context):
    return detect_iso_image(context)
