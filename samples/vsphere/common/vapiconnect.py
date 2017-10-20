"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'

import requests

from com.vmware.cis_client import Session

from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


def get_jsonrpc_endpoint_url(host):
    # The URL for the stub requests are made against the /api HTTP endpoint
    # of the vCenter system.
    return "https://{}/api".format(host)


def connect(host, user, pwd, skip_verification=False, cert_path=None, suppress_warning=True):
    """
    Create an authenticated stub configuration object that can be used to issue
    requests against vCenter.

    Returns a stub_config that stores the session identifier that can be used
    to issue authenticated requests against vCenter.
    """
    host_url = get_jsonrpc_endpoint_url(host)

    session = requests.Session()
    if skip_verification:
        session = create_unverified_session(session, suppress_warning)
    elif cert_path:
        session.verify = cert_path
    connector = get_requests_connector(session=session, url=host_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)

    return login(stub_config, user, pwd)


def login(stub_config, user, pwd):
    """
    Create an authenticated session with vCenter.

    Returns a stub_config that stores the session identifier that can be used
    to issue authenticated requests against vCenter.
    """
    # Pass user credentials (user/password) in the security context to
    # authenticate.
    user_password_security_context = create_user_password_security_context(user,
                                                                           pwd)
    stub_config.connector.set_security_context(user_password_security_context)

    # Create the stub for the session service and login by creating a session.
    session_svc = Session(stub_config)
    session_id = session_svc.create()

    # Successful authentication.  Store the session identifier in the security
    # context of the stub and use that for all subsequent remote requests
    session_security_context = create_session_security_context(session_id)
    stub_config.connector.set_security_context(session_security_context)

    return stub_config


def logout(stub_config):
    """
    Delete session with vCenter.
    """
    if stub_config:
        session_svc = Session(stub_config)
        session_svc.delete()


def create_unverified_session(session, suppress_warning=True):
    """
    Create a unverified session to disable the server certificate verification.
    This is not recommended in production code.
    """
    session.verify = False
    if suppress_warning:
        # Suppress unverified https request warnings
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    return session
