#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0.3+'

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsan.snapservice.data_protection_clients import DataProtectionClients

from com.vmware.snapservice.clusters_client import VirtualMachines


class QueryVirtualMachines(object):

    def __init__(self, snapservice_client, cluster_mo_id):
        self._snapservice_client = snapservice_client
        self._cluster_mo_id = cluster_mo_id

    def list(self):
        return self._snapservice_client.clusters.VirtualMachines.list(self._cluster_mo_id)

    def list_by_filter(self, filter_spec):
        return self._snapservice_client.clusters.VirtualMachines.list(self._cluster_mo_id, filter=filter_spec)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--cluster_mo_id',
                               action='store',
                               required=True,
                               help='Cluster MoRef ID where the virtual machine locates')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    vms = QueryVirtualMachines(clients.snapservice_client, args.cluster_mo_id)

    print("List of virtual machines:")
    print("----------------------------------------")
    vm_list = vms.list()
    for vm in vm_list.items:
        print(vm)
        print("----------------------------------------")

    # List filtered tasks
    print("List of filtered virtual machines:")
    print("----------------------------------------")
    # See the VirtualMachines.FilterSpec class constructor for other filters
    filter_spec = VirtualMachines.FilterSpec(vms={'vm-44'})
    filtered_vms = vms.list_by_filter(filter_spec)
    for vm in filtered_vms.items:
        print(vm)
        print("----------------------------------------")


if __name__ == '__main__':
    main()
