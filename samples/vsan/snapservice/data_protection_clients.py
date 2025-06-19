#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0.3+'

from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsan.snapservice.vsan_snapservice_client import create_snapservice_client
from samples.vsan.snapservice.vsan_snapservice_client import get_saml_token

from vmware.vapi.vsphere.client import create_vsphere_client


class DataProtectionClients(object):
    def __init__(self, args):
        _skipverification = True if args.skipverification else False
        _vc_session = get_unverified_session() if _skipverification else None
        self.vsphere_client = create_vsphere_client(server=args.server,
                                                    username=args.username,
                                                    password=args.password,
                                                    session=_vc_session)

        _ss_session = get_unverified_session() if _skipverification else None
        _saml_token = get_saml_token(vc=args.server, username=args.username, password=args.password,
                                     skip_verification=_skipverification)
        self.snapservice_client = create_snapservice_client(server=args.snapservice,
                                                            session=_ss_session,
                                                            saml_token=_saml_token)
