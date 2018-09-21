#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2018. All Rights Reserved.
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


import requests
from vmware.vapi.bindings.stub import ApiClient, StubFactoryBase
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

from vmware.vapi.vsphere.client import StubFactory

stub_config = StubConfigurationFactory.new_std_configuration(
    get_requests_connector(session=requests.session(), url='https://localhost/vapi'))
stub_factory = StubFactory(stub_config)
client = ApiClient(stub_factory)


def test_vcenter_client():
    assert hasattr(client, 'vcenter')
    assert isinstance(client.vcenter, StubFactoryBase)


def test_cluster_client():
    assert hasattr(client.vcenter, 'Cluster')


def test_datacenter_client():
    assert hasattr(client.vcenter, 'Datacenter')


def test_datastore_client():
    assert hasattr(client.vcenter, 'Datastore')


def test_deployment_client():
    assert hasattr(client.vcenter, 'Deployment')


def test_configuration_client():
    assert hasattr(client.content, 'Configuration')


def test_appliance_client():
    assert hasattr(client, 'appliance')
    assert isinstance(client.appliance, StubFactoryBase)


def test_content_client():
    assert hasattr(client, 'content')
    assert isinstance(client.content, StubFactoryBase)


def test_tagging_client():
    assert hasattr(client, 'tagging')
    assert isinstance(client.tagging, StubFactoryBase)


def test_ovf_client():
    assert hasattr(client.vcenter, 'ovf')
    assert isinstance(client.vcenter.ovf, StubFactoryBase)


def test_hvc_client():
    assert hasattr(client.vcenter, 'hvc')
    assert isinstance(client.vcenter.hvc, StubFactoryBase)


def test_inventory_client():
    assert hasattr(client.vcenter, 'inventory')
    assert isinstance(client.vcenter.inventory, StubFactoryBase)


def test_iso_client():
    assert hasattr(client.vcenter, 'iso')
    assert isinstance(client.vcenter.iso, StubFactoryBase)


def test_ovf_client():
    assert hasattr(client.vcenter, 'ovf')
    assert isinstance(client.vcenter.ovf, StubFactoryBase)


def test_vm_template_client():
    assert hasattr(client.vcenter, 'vm_template')
    assert isinstance(client.vcenter.vm_template, StubFactoryBase)


def test_appliance_update_client():
    assert hasattr(client.appliance, 'recovery')
    assert isinstance(client.appliance.recovery, StubFactoryBase)


def test_appliance_vmon_client():
    assert hasattr(client.appliance, 'vmon')
    assert isinstance(client.appliance.vmon, StubFactoryBase)


def test_compute_policy_client():
    assert hasattr(client.vcenter, 'compute')
    assert isinstance(client.vcenter.compute, StubFactoryBase)


def test_vm_compute_policy_client():
    assert hasattr(client.vcenter.vm, 'compute')
    assert isinstance(client.vcenter.vm.compute, StubFactoryBase)
