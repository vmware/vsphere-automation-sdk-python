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

__author__ = 'TODO: <your name and email>'
__vcenter_version__ = 'TODO: <compatible vcenter versions>'

from com.vmware.vcenter_client import VM
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session


"""
TODO: Sample description and prerequisites.
e.g. Demonstrates getting list of VMs present in vCenter

Sample Prerequisites:
    - vCenter
"""

# Create argument parser for standard inputs:
# server, username, password, cleanup and skipverification
parser = sample_cli.build_arg_parser()

# Add your custom input arguments
parser.add_argument('--vm_name',
                    action='store',
                    default='Sample_Default_VM_for_Simple_Testbed',
                    help='Name of the testing vm')

args = sample_util.process_cli_args(parser.parse_args())

# Skip server cert verification if needed.
# This is not recommended in production code.
session = get_unverified_session() if args.skipverification else None

# Connect to vSphere client
client = create_vsphere_client(server=args.server,
                               username=args.username,
                               password=args.password,
                               session=session)

# List VMs
filter_spec = VM.FilterSpec(names=set([args.vm_name]))
vms = client.vcenter.VM.list(filter_spec)
print(vms)
