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


import pyVim.task
from com.vmware.vcenter_client import (Folder)
from pyVmomi import vim

from samples.vsphere.vcenter.helper import datacenter_helper


def detect_vm_folder(context, datacenter_name, folder_name):
    """Find vm folder based on datacenter and folder name"""
    datacenter = datacenter_helper.get_datacenter(context.client,
                                                  datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.VIRTUAL_MACHINE,
                          names=set([folder_name]),
                          datacenters=set([datacenter])))
    if len(folder_summaries) > 0:
        folder = folder_summaries[0].folder
        print("Detected VM Folder '{}' as {}".format(folder_name, folder))
        context.testbed.entities['VM_FOLDER_IDS'][folder_name] = folder
        return True
    else:
        print("VM Folder '{}' missing in Datacenter {}".
              format(folder_name, datacenter_name))
        return False


def detect_vm_folders(context):
    """Find vm folder used to run vcenter samples"""
    context.testbed.entities['VM_FOLDER_IDS'] = {}

    folder1_name = context.testbed.config['VM_FOLDER1_NAME']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']

    folder2_name = context.testbed.config['VM_FOLDER2_NAME']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']

    return (detect_vm_folder(context, datacenter1_name, folder1_name) and
            detect_vm_folder(context, datacenter2_name, folder2_name))


def delete_vm_folder(context, datacenter_name, folder_name):
    """Delete vm folder from given datacenter"""
    for datacenter_mo in context.service_instance.content.rootFolder\
            .childEntity:
        if (isinstance(datacenter_mo, vim.Datacenter) and
                    datacenter_mo.name == datacenter_name):

            for folder_mo in datacenter_mo.vmFolder.childEntity:
                if folder_mo.name == folder_name:
                    print("Deleting Folder '{}' ({})' in Datacenter '{}' ({})".
                          format(folder_name, folder_mo._moId,
                                 datacenter_name, datacenter_mo._moId))
                    task = folder_mo.Destroy()
                    pyVim.task.WaitForTask(task)


def create_vm_folder(context, datacenter_name, folder_name):
    """Create vm folder in given datacenter"""
    datacenter = context.testbed.entities['DATACENTER_IDS'][datacenter_name]
    datacenter_mo = vim.Datacenter(datacenter, context.soap_stub)
    folder_mo = datacenter_mo.vmFolder.CreateFolder(folder_name)
    print("Created Folder '{}' ({}) in Datacenter '{}' ({})".
          format(folder_name, folder_mo._moId, datacenter_name, datacenter))
    return folder_mo._moId


def cleanup_vm_folders(context):
    """Delete vm folder after sample run"""
    folder1_name = context.testbed.config['VM_FOLDER1_NAME']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    delete_vm_folder(context, datacenter1_name, folder1_name)

    folder2_name = context.testbed.config['VM_FOLDER2_NAME']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    delete_vm_folder(context, datacenter2_name, folder2_name)


def setup_vm_folders(context):
    """Setup vm folder used to run vcenter samples"""
    folder1_name = context.testbed.config['VM_FOLDER1_NAME']
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    folder1 = create_vm_folder(context, datacenter1_name, folder1_name)

    folder2_name = context.testbed.config['VM_FOLDER2_NAME']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    folder2 = create_vm_folder(context, datacenter2_name, folder2_name)

    context.testbed.entities['VM_FOLDER_IDS'] = {
        folder1_name: folder1,
        folder2_name: folder2,
    }


def setup(context):
    setup_vm_folders(context)


def cleanup(context):
    cleanup_vm_folders(context)


def validate(context):
    return detect_vm_folders(context)
