#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2024 Broadcom. All Rights Reserved.
* The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom'
__copyright__ = 'Copyright (c) 2024 Broadcom. All Rights Reserved.'
__vcenter_version__ = '8.0.3+'

from pyVim.connect import SmartConnect

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common.ssl_helper import get_unverified_session

"""
With the single session functionality introduction,
in version 8.0.3, users are enabled to login only once and reuse
the session in vAPI and pyVmomi.

Demonstrates transfer of an authenticated session from pyVmomi
to a vAPI stub. The sample includes post transfer verification
via invocation of `vcenter.compute.Policies.list` operation,
which requires authenticated access.

Sample Prerequisites:
    - vCenter
"""


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Login with pyvmomi
    si = SmartConnect(host=args.server,
                      user=args.username,
                      pwd=args.password,
                      disableSslCertValidation=args.skipverification)
    print("Logged in through pyVmomi")

    # Acquire session_id
    session_id = si._GetStub().GetSessionId()
    print("Session ID acquired")

    # Reuse session_id in create_vsphere_client
    # A login will not be attempted when session_id is provided
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(args.server,
                                   session=session,
                                   session_id=session_id)
    print("Created vAPI client utilizing the pyVmomi session")

    result = client.vcenter.compute.Policies.list()
    if type(result) is list:
        print("Session has been successfully reused")
