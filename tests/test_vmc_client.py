#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
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

from vmware.vapi.vmc.client import create_vmc_client
from vmware.vapi.bindings.stub import ApiClient, StubFactoryBase

client = create_vmc_client('1234')


def test_orgs_client():
    assert hasattr(client, 'Orgs')


def test_locale_client():
    assert hasattr(client, 'Locale')


def test_account_link_client():
    assert hasattr(client.orgs, 'AccountLink')
    assert hasattr(client.orgs, 'account_link')
    assert isinstance(client.orgs.account_link, StubFactoryBase)


def test_providers_client():
    assert hasattr(client.orgs, 'Providers')


def test_reservations_client():
    assert hasattr(client.orgs, 'Reservations')
    assert hasattr(client.orgs, 'reservations')
    assert isinstance(client.orgs.reservations, StubFactoryBase)


def test_sddcs_client():
    assert hasattr(client.orgs, 'Sddcs')
    assert hasattr(client.orgs, 'sddcs')
    assert isinstance(client.orgs.sddcs, StubFactoryBase)


def test_sddcTemplates_client():
    assert hasattr(client.orgs, 'SddcTemplates')


def test_storage_client():
    assert hasattr(client.orgs, 'storage')
    assert isinstance(client.orgs.storage, StubFactoryBase)


def test_subscriptions_client():
    assert hasattr(client.orgs, 'Subscriptions')
    assert hasattr(client.orgs, 'subscriptions')
    assert isinstance(client.orgs.subscriptions, StubFactoryBase)


def test_tbrs_client():
    assert hasattr(client.orgs, 'tbrs')
    assert isinstance(client.orgs.tbrs, StubFactoryBase)


def test_tasks_client():
    assert hasattr(client.orgs, 'Tasks')
