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

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2023 VMware, Inc. All rights reserved.'
__vcenter_version__ = '8.0U2+'

import json
import requests

from vmware.vapi.data.serializers.cleanjson import DataValueConverter
from pyVmomi import vim
from pyVmomi.SoapAdapter import Serialize, Deserialize

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util

"""
Demonstrates conversion of data objects from the JSON based
automation runtime to the SOAP based runtime (pyVmomi) and vice
versa through the transcoder API, introduced in version `8.0.2.0`.

The current sample utilizes a `vim.vm.ConfigSpec` managed object,
present in bindings of both runtimes.

Sample Prerequisites:
    - vCenter
"""


class TranscoderStub(object):
    """
    Stub utilized for communicating to the transcoder API.
    """

    def __init__(self, server, session_id, version):
        self.server = server
        self.session_id = session_id
        self.version = version

    def transcode(self, body, to_json):
        """
        Transcodes and validates the integrity of a JSON or XML
        serialized data object.

        Transcoding is available from JSON or XML to JSON or XML
        for both cases.

        Transcoding to different encoding types is useful when
        utilizing the same data objects in a program involving
        SOAP and JSON based stacks/bindings.
        """
        resp = requests.post(url='https://{}/sdk/vim25/{}/transcoder'.format(self.server, self.version),
                             data=body,
                             headers={'Content-type': 'application/json' if not to_json else 'application/xml',
                                      'Accept': 'application/json' if to_json else 'application/xml',
                                      'vmware-api-session-id': self.session_id},  # alternatively use 'Cookie' header
                             # Skip server cert verification.
                             # This is not recommended in production code.
                             verify=False)

        return resp.content.decode()


def negotiate_version(server, client_desired_versions):
    """
    Invokes the System::Hello API, responsible for negotiating
    common parameters for API communication. The implementation
    selects mutually supported version from the choices passed
    in the request body.
    """
    resp = requests.post(url='https://{}/api/vcenter/system?action=hello'.format(server),
                         json={'api_releases': client_desired_versions},
                         # Skip server cert verification.
                         # This is not recommended in production code.
                         verify=False)

    return json.loads(resp.content.decode())['api_release']


def get_session_id(server, username, password, version):
    """
    Login through VI/JSON `SessionManager` API and acquire
    the `vmware-api-session-id` header.
    """
    resp = requests.post(url='https://{}/sdk/vim25/{}/SessionManager/SessionManager/Login'.format(server, version),
                         json=json.loads('{{"userName":"{}","password":"{}"}}'.format(username, password)),
                         # Skip server cert verification.
                         # This is not recommended in production code.
                         verify=False)
    return resp.headers.get('vmware-api-session-id')


def create_config_spec(datastore_name='datastore1',
                       name='sample-vm',
                       memory=4,
                       guest='guest',
                       annotation='Sample',
                       cpus=1):
    """
    Creates a pyVmomi `vim.vm.ConfigSpec` data object with
    arbitrarily populated fields.
    """
    config = vim.vm.ConfigSpec()
    config.annotation = annotation
    config.memoryMB = int(memory)
    config.guestId = guest
    config.name = name
    config.numCPUs = cpus
    files = vim.vm.FileInfo()
    files.vmPathName = '[' + datastore_name + ']'
    config.files = files
    return config


def convert_pyvmomi_obj_to_automation_dynamic_struct(transcoder, pyvmomi_obj):
    # Serialize pyVmomi object to XML
    xml_vm_config = Serialize(pyvmomi_obj)

    # Transcode XML to JSON
    json_vm_config = transcoder.transcode(xml_vm_config, to_json=True)
    print(json_vm_config)

    # Deserialize JSON to automation DynamicStructure
    struct_vm_config = DataValueConverter.convert_to_data_value(json_vm_config)
    print(type(struct_vm_config))
    return struct_vm_config


def convert_automation_dynamic_struct_to_pyvmomi_obj(transcoder, dynamic_struct):
    # Serialize DynamicStructure into JSON
    json_vm_config = DataValueConverter.convert_to_json(dynamic_struct)

    # Transcode JSON to XML
    xml_vm_config = transcoder.transcode(json_vm_config, to_json=False)
    print(xml_vm_config)

    # Deserialize XML to `vim.vm.ConfigSpec` data object
    config_vm_xml = Deserialize(xml_vm_config)
    print(type(config_vm_xml))


if __name__ == '__main__':
    # Disabling warnings is not recommended in production code.
    requests.packages.urllib3.disable_warnings()

    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Negotiating API release is necessary to use in APIs
    # utilizing inheritance based polymorphism - such as transcoder API.
    # Desired version is '8.0.2.0'
    version = negotiate_version(args.server, ['8.0.2.0'])

    session_id = get_session_id(args.server, args.username, args.password, version)

    transcoder = TranscoderStub(args.server, session_id, version)

    # Create SOAP vim.vm.ConfigSpec obj
    pyvmomi_vm_config = create_config_spec()

    dynamic_struct = convert_pyvmomi_obj_to_automation_dynamic_struct(transcoder, pyvmomi_vm_config)
    # Demonstrate conversion in the other direction
    convert_automation_dynamic_struct_to_pyvmomi_obj(transcoder, dynamic_struct)
