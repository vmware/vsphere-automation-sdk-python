#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013, 2016. All Rights Reserved.
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

import argparse

import requests

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from samples.vsphere.common import sso
from com.vmware.cis_client import Session
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.lib.connect import get_requests_connector
from samples.common.ssl_helper import get_unverified_context


class ConnectionWorkflow(object):
    """
    Demonstrates vAPI connection and service initialization callflow
    Step 1: Connect to the SSO URL and retrieve the SAML token.
    Step 2: Connect to the vapi service endpoint.
    Step 3: Use the SAML token to login to vAPI service endpoint.
    Step 4: Create a vAPI session.
    Step 5: Delete the vAPI session.
    Note: Use the lookup service print services sample to retrieve the SSO and vAPI service URLs
    """

    def __init__(self):
        self.vapi_url = None
        self.sts_url = None
        self.sso_username = None
        self.sso_password = None
        self.session = None
        self.skip_verification = False

    def options(self):
        self.argparser = argparse.ArgumentParser(description=self.__doc__)
        # setup the argument parser
        self.argparser.add_argument('-a', '--vapiurl', help='vAPI URL')
        self.argparser.add_argument('-s', '--stsurl', help='SSO URL')
        self.argparser.add_argument('-u', '--username', help='SSO username')
        self.argparser.add_argument('-p', '--password', help='SSO user password')
        self.argparser.add_argument('-v', '--skipverification', action='store_true',
                                    help='Do not verify server certificate')
        self.args = self.argparser.parse_args()   # parse all the sample arguments when they are all set

    def setup(self):
        self.vapi_url = self.args.vapiurl
        assert self.vapi_url is not None
        self.sts_url = self.args.stsurl
        assert self.sts_url is not None
        self.sso_username = self.args.username
        assert self.sso_username is not None
        self.sso_password = self.args.password
        assert self.sso_password is not None
        self.skip_verification = self.args.skipverification

    def execute(self):
        print('vapi_url: {0}'.format(self.vapi_url))
        # parse the URL and determine the scheme
        o = urlparse(self.vapi_url)
        assert o.scheme is not None
        if o.scheme.lower() != 'https':
            print('VAPI URL must be a https URL')
            raise Exception('VAPI URL must be a https URL')

        print('sts_url: {0}'.format(self.sts_url))
        print('Initialize SsoAuthenticator and fetching SAML bearer token...')
        authenticator = sso.SsoAuthenticator(self.sts_url)
        context = None
        if self.skip_verification:
            context = get_unverified_context()
        bearer_token = authenticator.get_bearer_saml_assertion(self.sso_username,
                                                               self.sso_password,
                                                               delegatable=True,
                                                               ssl_context=context)

        print('Creating SAML Bearer Security Context...')
        sec_ctx = create_saml_bearer_security_context(bearer_token)

        print('Connecting to VAPI provider and preparing stub configuration...')
        session = requests.Session()
        if self.skip_verification:
            session.verify = False
        connector = get_requests_connector(session=session, url=self.vapi_url)
        self.stub_config = StubConfigurationFactory.new_std_configuration(connector)

        connector.set_security_context(sec_ctx)
        self.stub_config = StubConfigurationFactory.new_std_configuration(connector)
        self.session = Session(self.stub_config)

        print('Login to VAPI endpoint and get the session_id...')
        self.session_id = self.session.create()

        print('Update the VAPI connection with session_id...')
        session_sec_ctx = create_session_security_context(self.session_id)
        connector.set_security_context(session_sec_ctx)

    def cleanup(self):
        if self.session_id is not None:
            self.disconnect()
            print('VAPI session disconnected successfully...')

    def disconnect(self):
        self.session.delete()


def main():
    connectionWorkflow = ConnectionWorkflow()
    connectionWorkflow.options()
    connectionWorkflow.setup()
    connectionWorkflow.execute()
    connectionWorkflow.cleanup()

# Start program
if __name__ == '__main__':
    main()
