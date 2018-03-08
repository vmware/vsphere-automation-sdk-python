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


from samples.vsphere.common.vim.file import (detect_directory,
                                             create_directory,
                                             delete_directory)


def setup(context):
    """Setup directories used by vcenter samples."""
    create_directory(context, 'Disk',
                     context.testbed.config['DISK_DATACENTER_NAME'],
                     context.testbed.config['DISK_DATASTORE_ROOT_PATH'])
    create_directory(context, 'CDROM ISO',
                     context.testbed.config['ISO_DATACENTER_NAME'],
                     context.testbed.config['ISO_DATASTORE_ROOT_PATH'])
    create_directory(context, 'Serial Port',
                     context.testbed.config['SERIAL_PORT_DATACENTER_NAME'],
                     context.testbed.config['SERIAL_PORT_DATASTORE_ROOT_PATH'])
    create_directory(context, 'Parallel Port',
                     context.testbed.config['PARALLEL_PORT_DATACENTER_NAME'],
                     context.testbed.config[
                         'PARALLEL_PORT_DATASTORE_ROOT_PATH'])
    create_directory(context, 'Floppy',
                     context.testbed.config['FLOPPY_DATACENTER_NAME'],
                     context.testbed.config['FLOPPY_DATASTORE_ROOT_PATH'])


def cleanup(context):
    """Cleanup directories after running vcenter samples"""
    delete_directory(context, 'Disk',
                     context.testbed.config['DISK_DATACENTER_NAME'],
                     context.testbed.config['DISK_DATASTORE_ROOT_PATH'])

    if context.option['DO_TESTBED_ISO_CLEANUP']:
        delete_directory(context, 'CDROM ISO',
                         context.testbed.config['ISO_DATACENTER_NAME'],
                         context.testbed.config['ISO_DATASTORE_ROOT_PATH'])

    delete_directory(context, 'Serial Port',
                     context.testbed.config['SERIAL_PORT_DATACENTER_NAME'],
                     context.testbed.config['SERIAL_PORT_DATASTORE_ROOT_PATH'])
    delete_directory(context, 'Parallel Port',
                     context.testbed.config['PARALLEL_PORT_DATACENTER_NAME'],
                     context.testbed.config[
                         'PARALLEL_PORT_DATASTORE_ROOT_PATH'])
    delete_directory(context, 'Floppy',
                     context.testbed.config['FLOPPY_DATACENTER_NAME'],
                     context.testbed.config['FLOPPY_DATASTORE_ROOT_PATH'])

    # Remove the top level Sample_Backends directory in the Datastore
    if context.option['DO_TESTBED_ISO_CLEANUP']:
        delete_directory(context, 'Backends',
                         context.testbed.config['BACKENDS_DATACENTER_NAME'],
                         context.testbed.config['BACKENDS_DATASTORE_ROOT_PATH'])


def validate(context):
    """Validate if all required directories exist to run vcenter samples"""
    return (
        detect_directory(context, 'Disk',
                         context.testbed.config['DISK_DATACENTER_NAME'],
                         context.testbed.config['DISK_DATASTORE_ROOT_PATH']) and
        detect_directory(context, 'CDROM ISO',
                         context.testbed.config['ISO_DATACENTER_NAME'],
                         context.testbed.config['ISO_DATASTORE_ROOT_PATH']) and
        detect_directory(context, 'Serial Port',
                         context.testbed.config['SERIAL_PORT_DATACENTER_NAME'],
                         context.testbed.config[
                             'SERIAL_PORT_DATASTORE_ROOT_PATH']) and
        detect_directory(context, 'Parallel Port',
                         context.testbed.config[
                             'PARALLEL_PORT_DATACENTER_NAME'],
                         context.testbed.config[
                             'PARALLEL_PORT_DATASTORE_ROOT_PATH']) and
        detect_directory(context, 'Floppy',
                         context.testbed.config['FLOPPY_DATACENTER_NAME'],
                         context.testbed.config['FLOPPY_DATASTORE_ROOT_PATH']))
