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

Demonstrates transfer of an authenticated session from vAPI to
a pyVmomi stub. The sample includes post transfer verification
via invocation of `sessionManager.SessionIsActive` operation,
which requires authenticated access.

Sample Prerequisites:
    - vCenter
"""


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Create session through vAPI
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(server=args.server,
                                   username=args.username,
                                   password=args.password,
                                   session=session)
    print("Logged in through vAPI vSphere client")

    # Acquire session_id
    session_id = client.get_session_id()
    print("Session ID acquired")

    # Reuse session_id in SmartConnect
    # A login will not be attempted when session_id is provided
    si = SmartConnect(host=args.server,
                      disableSslCertValidation=args.skipverification,
                      sessionId=session_id)
    print("Created pyVmomi stub utilizing the vAPI session")

    content = si.RetrieveContent()
    reused_session = content.sessionManager.currentSession
    result = content.sessionManager.SessionIsActive(reused_session.key, args.username)
    if result:
        print("Session has been successfully reused")
