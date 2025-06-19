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

from com.vmware.snapservice_client import StubFactory

from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.client.security_context_filter import LegacySecurityContextFilter
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

# In 80u3, the JSON-RPC endpoint is /api
# Since 9.0, it is changed to /snapservice
JSON_RPC_ENDPOINT = '/snapservice'


class SnapserviceStubFactory(StubFactory):
    def __init__(self, stub_config):
        StubFactory.__init__(self, stub_config)


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

        api_url = "https://" + server + JSON_RPC_ENDPOINT

        if bearer_token is None:
            raise "Please provide bearer_token to authenticate snapservice"
        sec_ctx = create_saml_bearer_security_context(bearer_token)

        stub_config = StubConfigurationFactory.new_std_configuration(
            get_requests_connector(
                session=session, url=api_url,
                provider_filter_chain=[
                    LegacySecurityContextFilter(
                        security_context=sec_ctx)]))

        stub_factory = SnapserviceStubFactory(stub_config)
        ApiClient.__init__(self, stub_factory)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()


def get_saml_token(vc, username, password, skip_verification=True):
    # Acquire token from sso.
    sso_url = 'https://' + vc + '/sts/STSService'
    authenticator = sso.SsoAuthenticator(sso_url)

    context = None
    if skip_verification:
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()

    # The token lifetime is 30 minutes.
    print("\n\nAcquire SAML token from PSC.\n")
    return authenticator.get_bearer_saml_assertion(username,
                                                   password,
                                                   token_duration=30 * 60,
                                                   delegatable=True,
                                                   ssl_context=context)


def create_snapservice_client(server, session, saml_token):
    """
    Helper method to create an instance of the snapservice client.
    Currently, snapservice only support bearer token to authenticate. So
    acquire bearer token from sso and then create the snapservice client.
    """

    return SnapserviceClient(session=session, server=server, bearer_token=saml_token)
