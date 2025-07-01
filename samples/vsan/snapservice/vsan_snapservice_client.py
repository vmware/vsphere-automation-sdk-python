#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2024 Broadcom. All Rights Reserved.
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

import requests
import ssl
from pyVim import sso

from com.vmware.snapservice.clusters_client import StubFactory as clusters_factory
from com.vmware.snapservice.info_client import StubFactory as info_factory
from com.vmware.snapservice.tasks_client import StubFactory as tasks_factory

from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.bindings.stub import StubFactoryBase
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

JSON_RPC_ENDPOINT = '/api'


class StubFactory(StubFactoryBase):

    def __init__(self, stub_config):
        StubFactoryBase.__init__(self, stub_config)
        self.snapservice.clusters = clusters_factory(stub_config)
        self.snapservice.info = info_factory(stub_config)
        self.snapservice.tasks = tasks_factory(stub_config)

    _attrs = {
        'snapservice': 'com.vmware.snapservice_client.StubFactory',
    }


class SnapserviceClient(ApiClient):
    """
    Snapservice Client class that provides access to stubs for all services in
    the snapservice API
    """

    def __init__(self, session, server, bearer_token):
        """
        Initialize SnapserviceClient by creating a parent stub factory instance
        of all snapservice components.

        :type  session: :class:`requests.Session`
        :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
        :type  server: :class:`str`
        :param server: snapservice appliance host name or IP address
        :type  bearer_token: :class:`str`
        :param bearer_token: SAML Bearer Token
        """
        if not session:
            session = requests.Session()
        self.session = session

        host_url = "https://" + server + JSON_RPC_ENDPOINT

        if bearer_token is None:
            raise "Please provide bearer_token to authenticate snapservice"
        sec_ctx = create_saml_bearer_security_context(bearer_token)

        stub_config = StubConfigurationFactory.new_std_configuration(
            get_requests_connector(
                session=session, url=host_url,
                provider_filter_chain=[
                    LegacySecurityContextFilter(
                        security_context=sec_ctx)]))

        stub_factory = StubFactory(stub_config)
        ApiClient.__init__(self, stub_factory)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()


def create_snapservice_client(server, vc, username, password, session,
                              skip_verification=True):
    """
    Helper method to create an instance of the snapservice client.
    Currently, snapservice only support bearer token to authenticate. So
    acqure bearer token from sso and then create the snapservice client.

    :type  server: :class:`str`
    :param server: snapservice appliance host name or IP address
    :type  vc: :class:`str`
    :param vc: vCenter server host name or IP address
    :type  username: :class:`str`
    :param username: username to the vCenter server
    :type  password: :class:`str`
    :param password: password of the username
    :type  session: :class:`requests.Session` or ``None``
    :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
    """
    # Acquire token from sso.
    sso_url = 'https://' + vc + '/sts/STSService'
    authenticator = sso.SsoAuthenticator(sso_url)

    context = None
    if skip_verification:
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()

    # The token lifetime is 30 minutes.
    print("\n\nAcquire SAML token from PSC.\n")
    saml_token = authenticator.get_bearer_saml_assertion(username,
                                                         password,
                                                         token_duration=30 * 60,
                                                         delegatable=True,
                                                         ssl_context=context)

    return SnapserviceClient(session=session, server=server, bearer_token=saml_token)
