#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2020. All Rights Reserved.
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
__vcenter_version__ = '7.0+'


from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter.topology_client import ReplicationStatus
from samples.vsphere.common import (sample_cli, sample_util)
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Description: Demonstrates listing of replication status for a vCenter Server.

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--node',
                    required=True,
                    help='Identifier of the vCenter or Platform Services'
                         ' Controller node. Identifier should be DNS'
                         ' resolvable name of the node')

args = sample_util.process_cli_args(parser.parse_args())

session = get_unverified_session() if args.skipverification else None

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

filter_spec = ReplicationStatus.FilterSpec({args.node})

print(vsphere_client.vcenter.topology.ReplicationStatus.list(filter_spec))
