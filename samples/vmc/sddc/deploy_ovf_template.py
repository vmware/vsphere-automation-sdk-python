#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2018. All Rights Reserved.
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
__vcenter_version__ = 'VMware Cloud on AWS'

from pprint import pprint as pp

from com.vmware.content.library_client import Item
from com.vmware.vcenter.ovf_client import LibraryItem
from com.vmware.vcenter_client import ResourcePool, Folder, Network
from com.vmware.vcenter.vm.hardware_client import Ethernet
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.id_generator import generate_random_uuid


class DeployOvfTemplate:
    """
    Demonstrates the workflow to deploy an OVF library item to
    a resource pool in VMware Cloud on AWS.
    Note: the sample needs an existing library item with an OVF template
    and an existing resource pool with resources for deploying the VM.
    """

    def __init__(self):

        self.vm_name = 'deployed-vm-' + str(generate_random_uuid())

        parser = sample_cli.build_arg_parser()
        required_args = parser.add_argument_group(
            'required arguments')
        required_args.add_argument('--libitemname',
                            required=True,
                            help='The name of the library item to deploy. '
                                 'The library item should contain an OVF package.')

        parser.add_argument('--vmname',
                            default=self.vm_name,
                            help='The name of the Virtual Machine to be deployed. '
                                 'Default: "{}"'.format(self.vm_name))

        parser.add_argument('--resourcepoolname',
                            default='Compute-ResourcePool',
                            help='The name of the resource pool to be used. '
                                 'Default: "Compute-ResourcePool"')

        parser.add_argument('--foldername',
                            default='Workloads',
                            help='The name of the folder to be used. '
                                 'Default: "Workloads"')

        parser.add_argument('--opaquenetworkname',
                            help='The name of the opaque network to be added '
                                 'to the deployed vm')

        args = sample_util.process_cli_args(parser.parse_args())

        self.vm_id = None
        self.lib_item_name = args.libitemname
        self.vm_name = args.vmname
        self.resourcepoolname = args.resourcepoolname
        self.foldername = args.foldername
        self.opaquenetworkname = args.opaquenetworkname
        self.cleardata = args.cleardata

        # Connect to vAPI Endpoint on vCenter Server
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password)

    def deploy_ovf_template(self):

        # Build the deployment target with resource pool ID and folder ID
        rp_filter_spec = ResourcePool.FilterSpec(names=set([self.resourcepoolname]))
        resource_pool_summaries = self.client.vcenter.ResourcePool.list(rp_filter_spec)
        if not resource_pool_summaries:
            raise ValueError("Resource pool with name '{}' not found".
                             format(self.resourcepoolname))
        resource_pool_id = resource_pool_summaries[0].resource_pool
        print('Resource pool ID: {}'.format(resource_pool_id))

        folder_filter_spec = Folder.FilterSpec(names=set([self.foldername]))
        folder_summaries = self.client.vcenter.Folder.list(folder_filter_spec)
        if not folder_summaries:
            raise ValueError("Folder with name '{}' not found".
                             format(self.foldername))
        folder_id = folder_summaries[0].folder
        print('Folder ID: {}'.format(folder_id))

        deployment_target = LibraryItem.DeploymentTarget(
            resource_pool_id=resource_pool_id,
            folder_id=folder_id
        )

        # Find the library item
        find_spec = Item.FindSpec(name=self.lib_item_name)
        lib_item_ids = self.client.content.library.Item.find(find_spec)
        if not lib_item_ids:
            raise ValueError("Library item with name '{}' not found".
                             format(self.lib_item_name))
        lib_item_id = lib_item_ids[0]
        print('Library item ID: {}'.format(lib_item_id))
        ovf_summary = self.client.vcenter.ovf.LibraryItem.filter(
            ovf_library_item_id=lib_item_id,
            target=deployment_target)
        print('Found an OVF template: {} to deploy.'.format(ovf_summary.name))

        # Build the deployment spec
        deployment_spec = LibraryItem.ResourcePoolDeploymentSpec(
            name=self.vm_name,
            annotation=ovf_summary.annotation,
            accept_all_eula=True,
            network_mappings=None,
            storage_mappings=None,
            storage_provisioning=None,
            storage_profile_id=None,
            locale=None,
            flags=None,
            additional_parameters=None,
            default_datastore_id=None)

        # Deploy the ovf template
        result = self.client.vcenter.ovf.LibraryItem.deploy(
            lib_item_id,
            deployment_target,
            deployment_spec,
            client_token=generate_random_uuid())

        # The type and ID of the target deployment is available in the deployment result.
        if result.succeeded:
            print('Deployment successful. VM Name: "{}", ID: "{}"'
                  .format(self.vm_name, result.resource_id.id))
            self.vm_id = result.resource_id.id
            error = result.error
            if error is not None:
                for warning in error.warnings:
                    print('OVF warning: {}'.format(warning.message))

        else:
            print('Deployment failed.')
            for error in result.error.errors:
                print('OVF error: {}'.format(error.message))

        # Add an opaque network portgroup to the deployed VM
        if self.opaquenetworkname:
            filter = Network.FilterSpec(
                names=set([self.opaquenetworkname]),
                types=set([Network.Type.OPAQUE_NETWORK]))
            network_summaries = self.client.vcenter.Network.list(filter=filter)
            if not network_summaries:
                raise ValueError("Opaque network {} can not find".format(
                    self.opaquenetworkname))
            network = network_summaries[0].network

            nic_create_spec = Ethernet.CreateSpec(
                start_connected=True,
                mac_type=Ethernet.MacAddressType.GENERATED,
                backing=Ethernet.BackingSpec(
                    type=Ethernet.BackingType.OPAQUE_NETWORK,
                    network=network))
            print('vm.hardware.Ethernet.create({}, {}) -> {}'.format(
                self.vm_id, nic_create_spec, network))
            nic = self.client.vcenter.vm.hardware.Ethernet.create(
                self.vm_id, nic_create_spec)

            nic_info = self.client.vcenter.vm.hardware.Ethernet.get(self.vm_id, nic)
            print('vm.hardware.Ethernet.get({}, {}) -> {}'.format(
                self.vm_id, nic, pp(nic_info)))

    def delete_vm(self):
        if self.cleardata:
            self.client.vcenter.VM.delete(self.vm_id)
            print('VM ({}) is deleted'.format(self.vm_id))


def main():
    deploy_ovf_sample = DeployOvfTemplate()
    deploy_ovf_sample.deploy_ovf_template()
    deploy_ovf_sample.delete_vm()


if __name__ == '__main__':
    main()
