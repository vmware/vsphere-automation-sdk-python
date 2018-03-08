#!/usr/bin/env python

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
__vcenter_version__ = '6.5+'

from com.vmware.vcenter.vm.hardware.boot_client import Device as BootDevice
from com.vmware.vcenter.vm.hardware_client import (
    Cpu, Memory, Disk, Ethernet, Cdrom, Serial, Parallel, Floppy, Boot)
from com.vmware.vcenter.vm.hardware_client import ScsiAddressSpec
from com.vmware.vcenter.vm_client import (Hardware, Power)
from com.vmware.vcenter_client import VM
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.helper import network_helper
from samples.vsphere.vcenter.helper import vm_placement_helper
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.vcenter.setup import testbed


class CreateExhaustiveVM(object):
    """
    Demonstrates how to create a exhaustive VM with the below configuration:
    3 disks, 2 nics, 2 vcpu, 2 GB, memory, boot=BIOS, 1 cdrom, 1 serial port,
    1 parallel port, 1 floppy, boot_device=[CDROM, DISK, ETHERNET])

    Sample Prerequisites:
        - datacenter
        - vm folder
        - resource pool
        - datastore
        - standard switch network
        - distributed switch network
        - An iso file on the datastore mentioned above
    """

    def __init__(self, client=None, placement_spec=None,
                 standard_network=None, distributed_network=None):
        self.client = client
        self.placement_spec = placement_spec
        self.standard_network = standard_network
        self.distributed_network = distributed_network
        self.vm_name = testbed.config['VM_NAME_EXHAUSTIVE']
        self.cleardata = None

        # Execute the sample in standalone mode.
        if not self.client:

            parser = sample_cli.build_arg_parser()
            parser.add_argument('-n', '--vm_name',
                                action='store',
                                help='Name of the testing vm')
            args = sample_util.process_cli_args(parser.parse_args())
            if args.vm_name:
                self.vm_name = args.vm_name
            self.cleardata = args.cleardata

            session = get_unverified_session() if args.skipverification else None
            self.client = create_vsphere_client(server=args.server,
                                                username=args.username,
                                                password=args.password,
                                                session=session)

    def run(self):
        # Get a placement spec
        datacenter_name = testbed.config['VM_DATACENTER_NAME']
        vm_folder_name = testbed.config['VM_FOLDER2_NAME']
        datastore_name = testbed.config['VM_DATASTORE_NAME']
        std_portgroup_name = testbed.config['STDPORTGROUP_NAME']
        dv_portgroup_name = testbed.config['VDPORTGROUP1_NAME']

        if not self.placement_spec:
            self.placement_spec = vm_placement_helper.get_placement_spec_for_resource_pool(
                self.client,
                datacenter_name,
                vm_folder_name,
                datastore_name)

        # Get a standard network backing
        if not self.standard_network:
            self.standard_network = network_helper.get_standard_network_backing(
                self.client,
                std_portgroup_name,
                datacenter_name)

        # Get a distributed network backing
        if not self.distributed_network:
            self.distributed_network = network_helper.get_distributed_network_backing(
                self.client,
                dv_portgroup_name,
                datacenter_name)

        """
        Create an exhaustive VM.

        Using the provided PlacementSpec, create a VM with a selected Guest OS
        and provided name.

        Create a VM with the following configuration:
        * Hardware Version = VMX_11 (for 6.0)
        * CPU (count = 2, coresPerSocket = 2, hotAddEnabled = false,
        hotRemoveEnabled = false)
        * Memory (size_mib = 2 GB, hotAddEnabled = false)
        * 3 Disks and specify each of the HBAs and the unit numbers
          * (capacity=40 GB, name=<some value>, spaceEfficient=true)
        * Specify 2 ethernet adapters, one using a Standard Portgroup backing and
        the
          other using a DISTRIBUTED_PORTGROUP networking backing.
          * nic1: Specify Ethernet (macType=MANUAL, macAddress=<some value>)
          * nic2: Specify Ethernet (macType=GENERATED)
        * 1 CDROM (type=ISO_FILE, file="os.iso", startConnected=true)
        * 1 Serial Port (type=NETWORK_SERVER, file="tcp://localhost/16000",
        startConnected=true)
        * 1 Parallel Port (type=HOST_DEVICE, startConnected=false)
        * 1 Floppy Drive (type=CLIENT_DEVICE)
        * Boot, type=BIOS
        * BootDevice order: CDROM, DISK, ETHERNET

        Use guest and system provided defaults for remaining configuration settings.
        """
        guest_os = testbed.config['VM_GUESTOS']
        iso_datastore_path = testbed.config['ISO_DATASTORE_PATH']
        serial_port_network_location = \
            testbed.config['SERIAL_PORT_NETWORK_SERVER_LOCATION']

        GiB = 1024 * 1024 * 1024
        GiBMemory = 1024

        vm_create_spec = VM.CreateSpec(
            guest_os=guest_os,
            name=self.vm_name,
            placement=self.placement_spec,
            hardware_version=Hardware.Version.VMX_11,
            cpu=Cpu.UpdateSpec(count=2,
                               cores_per_socket=1,
                               hot_add_enabled=False,
                               hot_remove_enabled=False),
            memory=Memory.UpdateSpec(size_mib=2 * GiBMemory,
                                     hot_add_enabled=False),
            disks=[
                Disk.CreateSpec(type=Disk.HostBusAdapterType.SCSI,
                                scsi=ScsiAddressSpec(bus=0, unit=0),
                                new_vmdk=Disk.VmdkCreateSpec(name='boot',
                                                             capacity=40 * GiB)),
                Disk.CreateSpec(new_vmdk=Disk.VmdkCreateSpec(name='data1',
                                                             capacity=10 * GiB)),
                Disk.CreateSpec(new_vmdk=Disk.VmdkCreateSpec(name='data2',
                                                             capacity=10 * GiB))
            ],
            nics=[
                Ethernet.CreateSpec(
                    start_connected=True,
                    mac_type=Ethernet.MacAddressType.MANUAL,
                    mac_address='11:23:58:13:21:34',
                    backing=Ethernet.BackingSpec(
                        type=Ethernet.BackingType.STANDARD_PORTGROUP,
                        network=self.standard_network)),
                Ethernet.CreateSpec(
                    start_connected=True,
                    mac_type=Ethernet.MacAddressType.GENERATED,
                    backing=Ethernet.BackingSpec(
                        type=Ethernet.BackingType.DISTRIBUTED_PORTGROUP,
                        network=self.distributed_network)),
            ],
            cdroms=[
                Cdrom.CreateSpec(
                    start_connected=True,
                    backing=Cdrom.BackingSpec(type=Cdrom.BackingType.ISO_FILE,
                                              iso_file=iso_datastore_path)
                )
            ],
            serial_ports=[
                Serial.CreateSpec(
                    start_connected=False,
                    backing=Serial.BackingSpec(
                        type=Serial.BackingType.NETWORK_SERVER,
                        network_location=serial_port_network_location)
                )
            ],
            parallel_ports=[
                Parallel.CreateSpec(
                    start_connected=False,
                    backing=Parallel.BackingSpec(
                        type=Parallel.BackingType.HOST_DEVICE)
                )
            ],
            floppies=[
                Floppy.CreateSpec(
                    backing=Floppy.BackingSpec(
                        type=Floppy.BackingType.CLIENT_DEVICE)
                )
            ],
            boot=Boot.CreateSpec(type=Boot.Type.BIOS,
                                 delay=0,
                                 enter_setup_mode=False
                                 ),
            # TODO Should DISK be put before CDROM and ETHERNET?  Does the BIOS
            # automatically try the next device if the DISK is empty?
            boot_devices=[
                BootDevice.EntryCreateSpec(BootDevice.Type.CDROM),
                BootDevice.EntryCreateSpec(BootDevice.Type.DISK),
                BootDevice.EntryCreateSpec(BootDevice.Type.ETHERNET)
            ]
        )
        print(
            '# Example: create_exhaustive_vm: Creating a VM using spec\n-----')
        print(pp(vm_create_spec))
        print('-----')

        vm = self.client.vcenter.VM.create(vm_create_spec)

        print("create_exhaustive_vm: Created VM '{}' ({})".format(self.vm_name,
                                                                  vm))

        vm_info = self.client.vcenter.VM.get(vm)
        print('vm.get({}) -> {}'.format(vm, pp(vm_info)))

        return vm

    def cleanup(self):
        vm = get_vm(self.client, self.vm_name)
        if vm:
            state = self.client.vcenter.vm.Power.get(vm)
            if state == Power.Info(state=Power.State.POWERED_ON):
                self.client.vcenter.vm.Power.stop(vm)
            elif state == Power.Info(state=Power.State.SUSPENDED):
                self.client.vcenter.vm.Power.start(vm)
                self.client.vcenter.vm.Power.stop(vm)
            print("Deleting VM '{}' ({})".format(self.vm_name, vm))
            self.client.vcenter.VM.delete(vm)


def main():
    create_exhaustive_vm = CreateExhaustiveVM()
    create_exhaustive_vm.cleanup()
    create_exhaustive_vm.run()
    if create_exhaustive_vm.cleardata:
        create_exhaustive_vm.cleanup()


if __name__ == '__main__':
    main()
