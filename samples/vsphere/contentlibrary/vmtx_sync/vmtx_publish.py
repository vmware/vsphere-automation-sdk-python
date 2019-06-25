#!/usr/bin/env python

"""
* *******************************************************
* Copyright VMware, Inc. 2019. All Rights Reserved.
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
__vcenter_version__ = '6.7U2+'

import time
import uuid

from com.vmware.content_client import LibraryModel
from com.vmware.content.library_client import (PublishInfo, SubscriptionInfo,
                                               StorageBacking,
                                               Subscriptions)
from com.vmware.vcenter.ovf_client import LibraryItem
from com.vmware.vcenter.vm_template_client import LibraryItems as VmtxLibraryItem

from pyVmomi import vim

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.id_generator import generate_random_uuid
from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common.vim.helpers.get_datastore_by_name import get_datastore_id
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from samples.vsphere.common.vim.helpers.vim_utils import (get_obj, get_obj_by_moId, delete_object)
from samples.vsphere.vcenter.helper.folder_helper import get_folder


class VmtxPublish(SampleBase):
    """
    Demonstrates the VMTX push sync workflow to publish and subscribe VMTX items.
    Note: the workflow needs an existing VC datastore with available storage.
    """

    SYNC_TIMEOUT_SEC = 60

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)

        self.servicemanager = None
        self.client = None
        self.helper = None
        self.datastore_name = None
        self.resource_pool_id = None
        self.folder_id = None

        self.pub_libs_to_clean = []
        self.sub_libs_to_clean = []
        self.vms_to_clean = []

    def _options(self):
        self.argparser.add_argument('-datacentername', '--datacentername', required=True,
                                    help='The name of the datacenter')
        self.argparser.add_argument('-datastorename', '--datastorename', required=True,
                                    help='The name of the datastore.')
        self.argparser.add_argument('-clustername', '--clustername', required=True,
                                    help='The name of the cluster to be used.')
        self.argparser.add_argument('-foldername', '--foldername', required=True,
                                    help='The name of the folder in the '
                                    'datacenter for creating a subscription')

    def _setup(self):
        self.datastore_name = self.args.datastorename
        self.cluster_name = self.args.clustername
        self.folder_name = self.args.foldername
        self.datacenter_name = self.args.datacentername
        self.servicemanager = self.get_service_manager()

        self.datastore_id = get_datastore_id(service_manager=self.servicemanager,
                                             datastore_name=self.datastore_name)
        self.client = ClsApiClient(self.servicemanager)
        self.helper = ClsApiHelper(self.client, self.skip_verification)
        session = get_unverified_session() if self.skip_verification else None
        self.vsphere_client = create_vsphere_client(server=self.server,
                                                    username=self.username,
                                                    password=self.password,
                                                    session=session)
        self.folder_id = get_folder(self.vsphere_client,
                                    self.datacenter_name,
                                    self.folder_name)
        self.storage_backings = self.helper.create_storage_backings(
            self.servicemanager, self.datastore_name)
        cluster_obj = get_obj(self.servicemanager.content,
                              [vim.ClusterComputeResource], self.cluster_name)
        self.resource_pool_id = cluster_obj.resourcePool._GetMoId()

    def _execute(self):
        self.create_new_subscription()
        self.create_subscription_from_existing_subscribed_library()

    def create_new_subscription(self):
        """
        Sample code for creating a new subscription for VMTX templates
        """

        # Create a published library and a new subscription
        pub_lib_name = "pub_lib_new_" + str(uuid.uuid4())
        pub_lib_id = self.create_published_library(pub_lib_name).id
        self.pub_libs_to_clean.append(pub_lib_id)
        sub_lib_name = "sub_lib_new_" + str(uuid.uuid4())
        subscription_id = self.create_subscription_new(pub_lib_id, sub_lib_name)

        # Get the subscribed library associated with the subscription
        subscription_info = self.client.subscriptions.get(pub_lib_id, subscription_id)
        sub_lib = self.client.library_service.get(subscription_info.subscribed_library)
        self.sub_libs_to_clean.append(sub_lib.id)

        # - Create a VMTX item on the published library
        # - Push-synchronize the subscription and verify the sync
        vm_name = "sample_vm_new_" + str(uuid.uuid4())
        vmtx_item_name = "sample_vmtx_item_existing_" + str(uuid.uuid4())
        vmtx_item_id = self.create_vmtx_item(pub_lib_id, vm_name, vmtx_item_name)
        self.client.local_library_service.publish(pub_lib_id)
        assert self.verify_vmtx_sync(sub_lib, vmtx_item_id)

    def create_subscription_from_existing_subscribed_library(self):
        """
        Sample code for converting existing Subscribed library
        to use a VMTX subscription
        """

        # Create a published library and get its publish URL
        pub_lib_name = "pub_lib_existing_" + str(uuid.uuid4())
        pub_lib = self.create_published_library(pub_lib_name)
        self.pub_libs_to_clean.append(pub_lib.id)
        pub_lib_url = pub_lib.publish_info.publish_url

        # Create a subscribed library
        sub_lib_name = "sub_lib_existing_" + str(uuid.uuid4())
        sub_lib = self.create_subscribed_library(pub_lib_url, sub_lib_name)
        self.create_subscription_for_existing_subscribed_library(pub_lib.id, sub_lib.id)

        # - Create a VMTX item on the published library
        # - Push-synchronize the subscription and verify the sync
        vm_name = "sample_vm_existing_" + str(uuid.uuid4())
        vmtx_item_name = "sample_vmtx_item_existing_" + str(uuid.uuid4())
        vmtx_item_id = self.create_vmtx_item(pub_lib.id, vm_name, vmtx_item_name)
        self.client.local_library_service.publish(pub_lib.id)
        assert self.verify_vmtx_sync(sub_lib, vmtx_item_id)

    def create_vmtx_item(self, pub_lib_id, vm_name, vmtx_item_name):
        # Upload OVF, create a VM, and use that VM to create a VMTX item
        ovf_item_id = self.create_ovf_template_item(pub_lib_id)
        source_vmtx_vm_id = self.create_vm(ovf_item_id, vm_name)
        self.vms_to_clean.append(source_vmtx_vm_id)
        vmtx_item_id = self.create_vmtx_item_from_vm(
            pub_lib_id, source_vmtx_vm_id, vmtx_item_name)
        return vmtx_item_id

    def create_published_library(self, pub_lib_name):
        pub_info = PublishInfo()
        pub_info.published = True
        # VMTX sync needs the authentication to be turned off
        pub_info.authentication_method = PublishInfo.AuthenticationMethod.NONE
        pub_spec = LibraryModel()
        pub_spec.name = pub_lib_name
        pub_spec.description = "Sample Published library"
        pub_spec.publish_info = pub_info
        pub_spec.type = pub_spec.LibraryType.LOCAL
        pub_spec.storage_backings = self.storage_backings

        pub_lib_id = self.client.local_library_service.create(
            create_spec=pub_spec, client_token=generate_random_uuid())
        print("Published library created, id: {0}".format(pub_lib_id))

        pub_lib = self.client.library_service.get(pub_lib_id)
        return pub_lib

    def create_subscribed_library(self, pub_lib_url, sub_lib_name):
        # Build the subscription information using the publish URL of the published
        # library

        sub_info = SubscriptionInfo()
        sub_info.authentication_method = SubscriptionInfo.AuthenticationMethod.NONE
        # on_demand = False for library and item level publish
        # on_demand = True for only item level publish, the library level
        #             publish will only sync the item metadata
        sub_info.on_demand = False
        sub_info.automatic_sync_enabled = True
        sub_info.subscription_url = pub_lib_url

        # Build the specification for the subscribed library
        sub_spec = LibraryModel()
        sub_spec.name = sub_lib_name
        sub_spec.type = sub_spec.LibraryType.SUBSCRIBED
        sub_spec.subscription_info = sub_info
        sub_spec.storage_backings = self.storage_backings

        sub_lib_id = self.client.subscribed_library_service.create(
            create_spec=sub_spec, client_token=generate_random_uuid())
        self.sub_libs_to_clean.append(sub_lib_id)
        print("Subscribed library created, id: {0}".format(sub_lib_id))
        sub_lib = self.client.subscribed_library_service.get(sub_lib_id)
        return sub_lib

    def create_subscription_new(self, pub_lib_id, sub_lib_name):
        # Create a new subscription. Such subscription is created on the published
        # library, and can be later used for a push-sync
        #
        # spec
        #   +--subscribed_library
        #        +--target: CREATE_NEW
        #        +--subscribed_library: DO NOT SPECIFY as this is new
        #        +--new_subscribed_library
        #            +--name, description, automatic_sync_enabled, on_demand
        #        +--location: LOCAL/REMOTE
        #        +--subscribed_library_vcenter: (VcenterInfo) DO NOT SPECIFY for location=LOCAL
        #        +--placement:
        #             +--Resource pool and folder for the VM
        #             +--network for the VM

        client_token = str(uuid.uuid4())
        spec = Subscriptions.CreateSpec()
        subscribed_library = Subscriptions.CreateSpecSubscribedLibrary()
        subscribed_library.location = Subscriptions.Location.LOCAL

        subscribed_library.target = \
            Subscriptions.CreateSpecSubscribedLibrary.Target.CREATE_NEW
        new_subscribed_library = Subscriptions.CreateSpecNewSubscribedLibrary()
        new_subscribed_library.name = sub_lib_name
        new_subscribed_library.description = "Sample subscribed library"

        backing = StorageBacking(StorageBacking.Type.DATASTORE, self.datastore_id)
        new_subscribed_library.storage_backings = [backing]

        new_subscribed_library.automatic_sync_enabled = False
        # on_demand = False for library and item level publish
        # on_demand = True for only item level publish, the library level
        #             publish will only sync the item metadata
        new_subscribed_library.on_demand = False
        subscribed_library.new_subscribed_library = new_subscribed_library

        placement = Subscriptions.CreateSpecPlacement()
        placement.resource_pool = self.resource_pool_id
        placement.folder = self.folder_id

        # Setting network to null implies that the subscription will use the
        # same network as the source VM
        # Warning - this may lead to failure if the same network is not
        # available to the subscriber
        placement.network = None

        subscribed_library.placement = placement
        spec.subscribed_library = subscribed_library

        subscription_id = self.client.subscriptions.create(
            pub_lib_id, spec, client_token)
        print("Subscription created, id: {0}".format(subscription_id))
        return subscription_id

    def create_subscription_for_existing_subscribed_library(self, pub_lib_id, sub_lib_id):
        # Create a subscription for an existing subscribed library. This subscription
        # and can be later used for a push-sync to that subscribed library
        #
        # spec
        #   +--subscribed_library
        #        +--target: USE_EXISTING
        #        +--subscribed_library: ID of existing subscribed library
        #        +--new_subscribed_library: DO NOT SPECIFY for target=USE_EXISTING
        #        +--location: LOCAL/REMOTE
        #        +--subscribed_library_vcenter: (VcenterInfo) DO NOT SPECIFY from location=LOCAL
        #        +--placement:
        #             +--Resource pool and folder for the VM
        #             +--network for the VM

        client_token = str(uuid.uuid4())
        spec = Subscriptions.CreateSpec()
        subscribed_library = Subscriptions.CreateSpecSubscribedLibrary()

        subscribed_library.target = \
            Subscriptions.CreateSpecSubscribedLibrary.Target.USE_EXISTING
        subscribed_library.subscribed_library = sub_lib_id
        subscribed_library.location = "LOCAL"
        placement = Subscriptions.CreateSpecPlacement()
        placement.resource_pool = self.resource_pool_id
        placement.folder = self.folder_id

        # Setting network to null implies that the subscription will use the
        # same network as the source VM
        # Warning - this may lead to failure if the same network is not
        # available to the subscriber
        placement.network = None

        subscribed_library.placement = placement
        spec.subscribed_library = subscribed_library

        subscription_id = self.client.subscriptions.create(
            pub_lib_id, spec, client_token)
        print("Subscription created id: {0}".format(subscription_id))
        return subscription_id

    def create_ovf_template_item(self, library_id):
        # Create an OVF item
        ovf_item_id = self.helper.create_library_item(library_id=library_id,
                                                      item_name='sample-ovf-item',
                                                      item_description='Sample OVF template',
                                                      item_type='ovf')
        print('Library item created id: {0}'.format(ovf_item_id))

        # Upload a VM template to the CL
        ovf_files_map = self.helper.get_ovf_files_map(ClsApiHelper.SIMPLE_OVF_RELATIVE_DIR)
        self.helper.upload_files(library_item_id=ovf_item_id, files_map=ovf_files_map)
        return ovf_item_id

    def create_vm(self, ovf_item_id, vm_name):
        # Deploy a VM using the given ovf template
        deployment_target = LibraryItem.DeploymentTarget(resource_pool_id=self.resource_pool_id)
        ovf_summary = self.client.ovf_lib_item_service.filter(ovf_library_item_id=ovf_item_id,
                                                              target=deployment_target)
        vm_id = self.deploy_ovf_template(ovf_item_id, ovf_summary, deployment_target, vm_name)
        print("Virtual Machine created, id: {0}".format(vm_id))
        return vm_id

    def deploy_ovf_template(self, lib_item_id, ovf_summary, deployment_target, vm_name):
        # Build the deployment spec
        deployment_spec = LibraryItem.ResourcePoolDeploymentSpec(
            name=vm_name, annotation=ovf_summary.annotation, accept_all_eula=True)

        # Deploy the ovf template
        result = self.client.ovf_lib_item_service.deploy(
            lib_item_id, deployment_target,
            deployment_spec, client_token=generate_random_uuid())
        if result.succeeded:
            vm_id = result.resource_id.id
            return vm_id
        else:
            print('Deployment failed.')
            for error in result.error.errors:
                print('OVF error: {}'.format(error.message))
            raise Exception('OVF deploy failed.')

    def create_vmtx_item_from_vm(self, library_id, source_vm_id, vmtx_item_name):
        # Create a VMTX item using the given VM as source
        create_spec = VmtxLibraryItem.CreateSpec()
        create_spec.source_vm = source_vm_id
        create_spec.library = library_id
        create_spec.name = vmtx_item_name
        create_spec.description = 'sample-vmtx-description'
        create_spec.placement = VmtxLibraryItem.CreatePlacementSpec()
        create_spec.placement.resource_pool = self.resource_pool_id
        vmtx_item_id = self.client.vmtx_service.create(create_spec)
        print("VMTX item created id: {0}".format(vmtx_item_id))
        return vmtx_item_id

    def verify_vmtx_sync(self, sub_lib, vmtx_item_id):
        # Wait until the VMTX item in the subscription is synchronized with
        # the one in the published library

        start_time = time.time()
        while time.time() - start_time < self.SYNC_TIMEOUT_SEC:
            sub_item_ids = self.client.library_item_service.list(sub_lib.id)
            # Only vmtx item will be synced using the push mechanism, so check
            # the length to be one
            if len(sub_item_ids) == 1:
                source_id = self.client.library_item_service.get(
                    sub_item_ids[0]).source_id
                # Verify that the source for the VMTX item in the subscribed
                # library is the VMTX item in the published library
                if source_id == vmtx_item_id:
                    return True
                else:
                    print("VMTX source item id mismatch")
                    return False
            # Give some more time for sync
            time.sleep(1)

        print("Timed out while waiting for sync")
        return False

    def _cleanup(self):
        for lib_id in self.pub_libs_to_clean:
            print("deleting published library: {0}".format(lib_id))
            self.client.local_library_service.delete(lib_id)
        for lib_id in self.sub_libs_to_clean:
            print("deleting subscribed library: {0}".format(lib_id))
            self.client.subscribed_library_service.delete(lib_id)
        for vm_id in self.vms_to_clean:
            vm_obj = get_obj_by_moId(self.servicemanager.content,
                                     [vim.VirtualMachine], vm_id)
            delete_object(self.servicemanager.content, vm_obj)


def main():
    sample = VmtxPublish()
    sample.main()


if __name__ == '__main__':
    main()
