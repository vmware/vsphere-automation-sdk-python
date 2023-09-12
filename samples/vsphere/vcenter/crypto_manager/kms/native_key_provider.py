#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2023. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""


__author__ = 'Kiril Karaatanssov <kkaraatanassov@vmware.com>'
__vcenter_version__ = '7.0.2.0'


import requests
import sys
import time

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session

from vmware.vapi.vsphere.client import create_vsphere_client, VsphereClient
from com.vmware.vcenter.crypto_manager import kms_client
from com.vmware.vapi.std.errors_client import AlreadyExists
from pyVim.connect import SmartConnect
from pyVmomi import vim

"""
Demonstrates common operations with vCenter Native Key Provider functionality.

This sample is a simple scenario that provisions native key provider, backs it
up (which also activates it), deletes it, restores from back up, sets the new
provider as default, reverts the defaults and deletes the new key provider.

There is one tricky part with export of the key provider data. This requires
raw HTTP request to download the p12 key provider data with HTTP Authorization
Bearer header and the token value from the API.

The APIs are described under:
https://developer.vmware.com/apis/vsphere-automation/latest/vcenter/crypto_manager/kms.providers/

Setting and reading the default key provider is achieved using the
CryptoMangerKmip API:
https://developer.vmware.com/apis/vi-json/latest/crypto-manager-kmip/

Sample Prerequisites:
    - vCenter
    - Python 3.9
"""


def get_kms_providers(client: VsphereClient) -> kms_client.Providers:
    return vsphere_client.vcenter.crypto_manager.kms.Providers


def print_kms_configurations(kmsProviders: kms_client.Providers):
    for provider in kmsProviders.list():
        print(f"Native Key Provider summary: {provider}")
        print(f"Native Key Provider details: {kmsProviders.get(provider.provider)}")
        print()


def connect(host: str, user: str, pwd: str, insecure: bool) -> tuple[VsphereClient, vim.ServiceInstance]:
    session = requests.session()
    session = get_unverified_session() if insecure else None
    vsphere_client = create_vsphere_client(host, user, pwd, session=session)
    si = SmartConnect(host=host, user=user, pwd=pwd, disableSslCertValidation=insecure)
    return vsphere_client, si


# Create argument parser for standard inputs:
# server, username, password, cleanup and skipverification
parser = sample_cli.build_arg_parser()

# Add your custom input arguments
parser.add_argument('--key_provider',
                    action='store',
                    default='native_kms',
                    help='Name/ID of native key provider to use in the demo scenario.')

parser.add_argument('--export_password',
                    action='store',
                    default='$up3r$3cr3t!',
                    help='Password ot use in import and export of key provider.')


args = sample_util.process_cli_args(parser.parse_args())

# Skip server cert verification if needed.
# This is not recommended in production code.

# Connect to vSphere
vsphere_client, si = connect(args.server, args.username, args.password, args.skipverification)

# Initialize stubs

# Automation API Kms.Providers
kmsProviders = get_kms_providers(vsphere_client)

# PyVmomi vim.encryption.CryptoManagerKmip
cm = si.content.cryptoManager
if not isinstance(cm, vim.encryption.CryptoManagerKmip):
    raise TypeError("Expected CryptoManagerKmip")

# read demo args
provider_name = args.key_provider
password = args.export_password


# Print baseline state
print_kms_configurations(kmsProviders=kmsProviders)

print("Create Native Key Provider.")
try:
    kmsProviders.create(kmsProviders.CreateSpec(provider_name,
                constraints=kmsProviders.ConstraintsSpec(tpm_required=False)))
except AlreadyExists as ex:
    print(f"Nice Native Key Provider is already set up: {ex}")

print_kms_configurations(kmsProviders=kmsProviders)


print('Backup Native Key Provider')
res = kmsProviders.export(kmsProviders.ExportSpec(provider=provider_name,
                                                  password=password))

# Download the back up data to complete the backup process. Without this
# request the state of the provider will indicate it is not ready for use as it
# is not backed up.
url = res.location.url
token = res.location.download_token
response = requests.post(
    url,
    headers={'Authorization': 'Bearer %s' % token.token},
    verify=False)
if not response.status_code == 200:
    print(f"Backup failed {response}")
    sys.exit(1)
p12data = response.content
print(f'Backup completed ok')

print_kms_configurations(kmsProviders=kmsProviders)

print("Delete Native Key Provider")
kmsProviders.delete(provider=provider_name)

print_kms_configurations(kmsProviders=kmsProviders)

# Restore Native Key Provider
ir = kmsProviders.import_provider(kmsProviders.ImportSpec(config=p12data,
                password=password,
                constraints=kmsProviders.ConstraintsSpec(tpm_required=False)))
print(f'Restore Native Key Provider: {ir}')

# vCenter seems to need respite to set the key provider to all hosts. Immediate
# read shows warnings.
time.sleep(1)
print_kms_configurations(kmsProviders=kmsProviders)

# Set default Key Native Provider via pyVMOMI CryptoManagerKmip

# Keep the current setting for default key provider
defaultProvider = cm.GetDefaultKmsCluster()
print(f"Default Key Provider {defaultProvider}")

# Convert Automation API ID (str) to PyVMOMI KeyProviderId
providerId = vim.encryption.KeyProviderId()
providerId.id = provider_name

# Set the new default
cm.SetDefaultKmsCluster(clusterId=providerId)
print(f"Updated default key provider to {cm.GetDefaultKmsCluster()}")

cm.SetDefaultKmsCluster(clusterId=defaultProvider)
print(f"Restored default key provider to {cm.GetDefaultKmsCluster()}")

print("Delete Native Key Provider")
kmsProviders.delete(provider=provider_name)

print("Done.")
