"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

import vsphere.samples.vcenter.setup.backend_directory as backend_directory
import vsphere.samples.vcenter.setup.cluster as cluster
import vsphere.samples.vcenter.setup.datacenter as datacenter
import vsphere.samples.vcenter.setup.datastore as datastore
import vsphere.samples.vcenter.setup.floppy_image as floppy_image
import vsphere.samples.vcenter.setup.folder as folder
import vsphere.samples.vcenter.setup.host as host
import vsphere.samples.vcenter.setup.iso_image as iso_image
import vsphere.samples.vcenter.setup.network as network

"""
Setup Simple Testbed: Which provides the prerequisites for using the VM API
Inputs:
* IP address or hostname of vCenter
* IP address of 2 hosts
* (IP address,server path) of a NFS Server

* Assumes that all resources will be created off the root folders
  within each datacenter.  No need to recursively traverse across
  different folders looking for the entities.

* Two Datacenters
  * "Sample DC 1"
  * "Sample DC 2"
* One Cluster
  * "Sample Cluster"
* 2 host environment
  * 1 host in Sample Cluster in Sample DC 1
  * One network adapter per Host
  * Name of Host will be the IP address
* 3 Datastores, any constraints?
  * Shared NFS Datastore
    * "Shared NFS Volume"
  * 2 Local VMFS Datastore (name the datastores based on the host)
    * "Local VMFS Datastore on <host_ip>"
* 1 Standard Portgroups (verify)
    * "VM Network" (the default created per host)
* 1 Distributed Switch ("DSwitch 1")
  * 1 non-uplink DvPortgroups
    * static ("Static Portgroup on DSwitch 1")
* 2 created VM Folder, one in each Datacenter
  * "Sample VM Folder 1"
  * "Sample VM Folder 2"
* Put an ISO image on a Datastore
* Put a Floppy image on a Datastore
"""


def setup(context):
    print('Setup Testbed Start')
    datacenter.setup(context)
    folder.setup(context)
    cluster.setup(context)
    host.setup(context)
    datastore.setup(context)
    network.setup(context)
    backend_directory.setup(context)
    iso_image.setup(context)
    floppy_image.setup(context)
    print('Setup Testbed Complete\n')


def cleanup(context):
    print('Cleanup Testbed Start')
    floppy_image.cleanup(context)
    if context.option['DO_TESTBED_ISO_CLEANUP']:
        iso_image.cleanup(context)
    backend_directory.cleanup(context)
    network.cleanup(context)
    datastore.cleanup(context)
    host.cleanup(context)
    cluster.cleanup(context)
    folder.cleanup(context)
    datacenter.cleanup(context)
    print('Cleanup Testbed Complete\n')


def validate(context):
    print('Validating and Detecting Resources in Testbed')
    r = (datacenter.validate(context) and
         folder.validate(context) and
         cluster.validate(context) and
         host.validate(context) and
         datastore.validate(context) and
         network.validate(context) and
         backend_directory.validate(context) and
         iso_image.validate(context) and
         floppy_image.validate(context)
         )
    if r:
        print('==> Testbed validated')
        return True
    else:
        print('==> Testbed has errors')
        return False
