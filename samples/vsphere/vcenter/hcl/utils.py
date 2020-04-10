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

__author__ = 'VMware, Inc.'
__vcenter_version__ = '7.0+'

import requests

from com.vmware.cis_client import Session

from samples.vsphere.common.ssl_helper import get_unverified_session
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter
from vmware.vapi.security.user_password import \
    create_user_password_security_context


"""
Creates a session and returns the stub configuration
"""


def get_configuration(server, username, password, skipVerification):
    session = get_unverified_session() if skipVerification else None
    if not session:
        session = requests.Session()
    host_url = "https://{}/api".format(server)
    sec_ctx = create_user_password_security_context(username,
                                                    password)
    session_svc = Session(
        StubConfigurationFactory.new_std_configuration(
            get_requests_connector(
                session=session, url=host_url,
                provider_filter_chain=[
                    LegacySecurityContextFilter(
                        security_context=sec_ctx)])))
    session_id = session_svc.create()
    print("Session ID : ", session_id)
    sec_ctx = create_session_security_context(session_id)
    stub_config = StubConfigurationFactory.new_std_configuration(
        get_requests_connector(
            session=session, url=host_url,
            provider_filter_chain=[
                LegacySecurityContextFilter(
                    security_context=sec_ctx)]))
    return stub_config
