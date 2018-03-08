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

from com.vmware.vcenter_client import (Datacenter, Folder)


def folder_list_datacenter_folder(context):
    return context.client.vcenter.Folder.list(Folder.FilterSpec(type=Folder.Type.DATACENTER))


def detect_datacenter(context, datacenter_name):
    """Find the datacenter with the given name"""
    names = set([datacenter_name])
    datacenter_summaries = context.client.vcenter.Datacenter.list(
        Datacenter.FilterSpec(names=names))
    if len(datacenter_summaries) > 0:
        datacenter = datacenter_summaries[0].datacenter
        print("Detected Datacenter '{}' as {}".
              format(datacenter_name, datacenter))
        context.testbed.entities['DATACENTER_IDS'][datacenter_name] = datacenter
        return True
    else:
        print("Datacenter '{}' missing".format(datacenter_name))
        return False


def detect_datacenters(context):
    """Find datacenters to run the vcenter samples"""
    context.testbed.entities['DATACENTER_IDS'] = {}

    # Look for the two datacenters
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']

    return (detect_datacenter(context, datacenter1_name) and
            detect_datacenter(context, datacenter2_name))


def cleanup_datacenters(context):
    """Cleanup datacenters after sample run"""

    # Look for the two datacenters
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    names = set([datacenter1_name, datacenter2_name])

    datacenter_summaries = context.client.vcenter.Datacenter.list(
        Datacenter.FilterSpec(names=names))
    print("Found {} Datacenters matching names {}".
          format(len(datacenter_summaries), ", ".
                 join(["'{}'".format(n) for n in names])))

    for datacenter_summary in datacenter_summaries:
        datacenter = datacenter_summary.datacenter
        print("Deleting Datacenter '{}' ({})".
              format(datacenter, datacenter_summary.name))
        context.client.vcenter.Datacenter.delete(datacenter, force=True)


def setup_datacenters(context):
    """Create datacenters for running vcenter samples"""
    # Find a Folder in which to put the Datacenters
    folder_summaries = folder_list_datacenter_folder(context)
    folder = folder_summaries[0].folder
    print("Creating datacenters in Folder '{}' ({})".
          format(folder, folder_summaries[0].name))

    # Create first datacenter
    datacenter1_name = context.testbed.config['DATACENTER1_NAME']
    datacenter1 = context.client.vcenter.Datacenter.create(
        Datacenter.CreateSpec(name=datacenter1_name, folder=folder)
    )
    print("Created Datacenter '{}' ({})".format(datacenter1, datacenter1_name))

    # Create second datacenter
    datacenter2_name = context.testbed.config['DATACENTER2_NAME']
    datacenter2 = context.client.vcenter.Datacenter.create(
        Datacenter.CreateSpec(name=datacenter2_name, folder=folder)
    )
    print("Created Datacenter '{}' ({})".format(datacenter2, datacenter2_name))

    # Save datacenter name to identifier mappings for later use
    context.testbed.entities['DATACENTER_IDS'] = {
        datacenter1_name: datacenter1,
        datacenter2_name: datacenter2
    }


def cleanup(context):
    cleanup_datacenters(context)


def setup(context):
    setup_datacenters(context)


def validate(context):
    return detect_datacenters(context)
