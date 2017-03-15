"""
* *******************************************************
* Copyright VMware, Inc. 2013, 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2013, 2016 VMware, Inc. All rights reserved.'

from pyVim.connect import SmartConnect, Disconnect
from samples.vsphere.common import vapiconnect

from samples.vsphere.common.ssl_helper import get_unverified_context


class ServiceManager(object):
    """
    Manages Vim and vAPI services on a management node.
    """
    def __init__(self, server, username, password, skip_verification):

        self.server_url = server
        self.username = username
        self.password = password
        self.skip_verification = skip_verification
        self.vapi_url = None
        self.vim_url = None
        self.session = None
        self.session_id = None
        self.stub_config = None
        self.si = None
        self.content = None
        self.vim_uuid = None

    def connect(self):
        # Connect to vAPI Endpoint on vCenter Server system
        self.stub_config = vapiconnect.connect(host=self.server_url,
                                               user=self.username,
                                               pwd=self.password,
                                               skip_verification=self.skip_verification)

        # Connect to VIM API Endpoint on vCenter Server system
        context = None
        if self.skip_verification:
            context = get_unverified_context()
        self.si = SmartConnect(host=self.server_url,
                               user=self.username,
                               pwd=self.password,
                               sslContext=context)
        assert self.si is not None

        # Retrieve the service content
        self.content = self.si.RetrieveContent()
        assert self.content is not None
        self.vim_uuid = self.content.about.instanceUuid

    def disconnect(self):
        print('disconnecting the session')
        vapiconnect.logout(self.stub_config)
        Disconnect(self.si)
