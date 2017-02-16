#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""


__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.0+'

from pprint import pprint
import requests

from com.vmware.cis_client import Session
from com.vmware.vcenter_client import Datacenter
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vapiconnect import create_unverified_session
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common import sso


class EmbeddedPscSsoWorkflow(object):
    """
    Demonstrates how to Login to vCenter vAPI service with
    embedded Platform Services Controller.
    """

    def __init__(self):
        self.server = None
        self.username = None
        self.password = None
        self.session = None
        self.session_id = None
        self.skip_verification = False

    def setup(self):
        self.server, self.username, self.password, _, self.skip_verification = \
            parse_cli_args()

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'embedded Platform Services Controller')

        # Since the platform services controller is embedded, the sso server
        # is the same as the vCenter server.
        ssoUrl = 'https://{}/sts/STSService'.format(self.server)

        print('\nStep 1: Connect to the Single Sign-On URL and '
              'retrieve the SAML bearer token.')

        authenticator = sso.SsoAuthenticator(ssoUrl)
        context = None
        if self.skip_verification:
            context = get_unverified_context()
        bearer_token = authenticator.get_bearer_saml_assertion(
            self.username,
            self.password,
            delegatable=True,
            ssl_context=context)

        # Creating SAML Bearer Security Context
        sec_ctx = create_saml_bearer_security_context(bearer_token)

        print('\nStep 2. Login to vAPI services using the SAML bearer token.')

        # The URL for the stub requests are made against the /api HTTP endpoint
        # of the vCenter system.
        vapi_url = 'https://{}/api'.format(self.server)

        # Create an authenticated stub configuration object that can be used to
        # issue requests against vCenter.
        session = requests.Session()
        if self.skip_verification:
            session = create_unverified_session(session)
        connector = get_requests_connector(session=session, url=vapi_url)
        connector.set_security_context(sec_ctx)
        stub_config = StubConfigurationFactory.new_std_configuration(
            connector)
        self.session = Session(stub_config)

        # Login to VAPI endpoint and get the session_id
        self.session_id = self.session.create()

        # Update the VAPI connection with session_id
        session_sec_ctx = create_session_security_context(self.session_id)
        connector.set_security_context(session_sec_ctx)

        print('\nStep 3: List available datacenters using the vAPI services')

        datacenter_svc = Datacenter(stub_config)
        pprint(datacenter_svc.list())

        self.session.delete()
        print('VAPI session disconnected successfully...')


def main():
    embedded_psc_sso_workflow = EmbeddedPscSsoWorkflow()
    embedded_psc_sso_workflow.setup()
    embedded_psc_sso_workflow.run()


# Start program
if __name__ == '__main__':
    main()
