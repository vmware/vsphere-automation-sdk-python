#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2016-2023. All Rights Reserved.
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
__vcenter_version__ = '6.0+'

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from com.vmware.vcenter.ovf_client import LibraryItem
from pyVmomi import vim
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.service_manager import ServiceManager
from samples.vsphere.common.vim.helpers.vim_utils import (
    get_obj, get_obj_by_moId, poweron_vm, poweroff_vm, delete_object)
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper


class DeployOvfTemplate(SampleBase):
    """
    Demonstrates the workflow to deploy an OVF library item to a resource pool.
    Note: the sample needs an existing library item with an OVF template
    and an existing cluster with resources for deploying the VM.
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None
        self.client = None
        self.helper = None
        self.cluster_name = None
        self.lib_item_name = None
        self.vm_obj = None
        self.vm_name = None

    def _options(self):
        self.argparser.add_argument('-n',
                                    '--vm_name',
                                    help='Name of the testing vm.')
        self.argparser.add_argument('-clustername',
                                    '--clustername',
                                    help='The name of the cluster to be used.')
        self.argparser.add_argument('-libitemname',
                                    '--libitemname',
                                    help='The name of the library item to deploy.'
                                 'The library item should contain an OVF package.')

    def _setup(self):
        # Default VM name
        self.vm_name = 'vm-' + str(generate_random_uuid())

        self.cluster_name = self.args.clustername
        assert self.cluster_name is not None

        self.lib_item_name = self.args.libitemname
        assert self.lib_item_name is not None

        if not self.servicemanager:
            self.servicemanager = self.get_service_manager()

        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)

    def _execute(self):
        # Find the cluster's resource pool moid
        cluster_obj = get_obj(self.servicemanager.content,
                              [vim.ClusterComputeResource], self.cluster_name)
        assert cluster_obj is not None
        print("Cluster Moref: {0}".format(cluster_obj))

        deployment_target = LibraryItem.DeploymentTarget(
            resource_pool_id=cluster_obj.resourcePool._GetMoId())
        lib_item_id = self.helper.get_item_id_by_name(self.lib_item_name)
        assert lib_item_id
        ovf_summary = self.client.ovf_lib_item_service.filter(ovf_library_item_id=lib_item_id,
                                                              target=deployment_target)
        print('Found an OVF template :{0} to deploy.'.format(ovf_summary.name))

        # Deploy the ovf template
        self.deploy_ovf_template(lib_item_id, ovf_summary, deployment_target)

    def deploy_ovf_template(self, lib_item_id, ovf_summary, deployment_target):
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
        result = self.client.ovf_lib_item_service.deploy(lib_item_id,
                                                         deployment_target,
                                                         deployment_spec,
                                                         client_token=generate_random_uuid())

        # The type and ID of the target deployment is available in the deployment result.
        if result.succeeded:
            print('Deployment successful. Result resource: {0}, ID: {1}'
                  .format(result.resource_id.type, result.resource_id.id))
            self.vm_id = result.resource_id.id
            error = result.error
            if error is not None:
                for warning in error.warnings:
                    print('OVF warning: {}'.format(warning.message))

            # Power on the VM and wait  for the power on operation to be completed
            self.vm_obj = get_obj_by_moId(self.servicemanager.content,
                                          [vim.VirtualMachine], self.vm_id)
            assert self.vm_obj is not None
            poweron_vm(self.servicemanager.content, self.vm_obj)

        else:
            print('Deployment failed.')
            for error in result.error.errors:
                print('OVF error: {}'.format(error.message))

    def _cleanup(self):
        if self.vm_obj is not None:
            # Power off the VM and wait for the power off operation to complete
            poweroff_vm(self.servicemanager.content, self.vm_obj)
            # Delete the VM
            delete_object(self.servicemanager.content, self.vm_obj)


def main():
    deploy_ovf_sample = DeployOvfTemplate()
    deploy_ovf_sample.main()


if __name__ == '__main__':
    main()
