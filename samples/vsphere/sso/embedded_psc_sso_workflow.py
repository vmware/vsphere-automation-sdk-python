#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.0+'

import requests
from com.vmware.cis.tagging_client import (Category, CategoryModel)
from com.vmware.cis_client import Session
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import sso
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vapiconnect import create_unverified_session


class EmbeddedPscSsoWorkflow(object):
    """
    Demonstrates how to Login to vCenter vAPI service with
    embedded Platform Services Controller.
    """

    def __init__(self):
        self.args = None
        self.session = None
        self.session_id = None
        self.category_svc = None
        self.category_id = None

    def setup(self):
        parser = sample_cli.build_arg_parser()
        self.args = sample_util.process_cli_args(parser.parse_args())

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'embedded Platform Services Controller')

        # Since the platform services controller is embedded, the sso server
        # is the same as the vCenter server.
        ssoUrl = 'https://{}/sts/STSService'.format(self.args.server)

        print('\nStep 1: Connect to the Single Sign-On URL and '
              'retrieve the SAML bearer token.')

        authenticator = sso.SsoAuthenticator(ssoUrl)
        context = None
        if self.args.skipverification:
            context = get_unverified_context()
        bearer_token = authenticator.get_bearer_saml_assertion(
            self.args.username,
            self.args.password,
            delegatable=True,
            ssl_context=context)

        # Creating SAML Bearer Security Context
        sec_ctx = create_saml_bearer_security_context(bearer_token)

        print('\nStep 2. Login to vAPI services using the SAML bearer token.')

        # The URL for the stub requests are made against the /api HTTP endpoint
        # of the vCenter system.
        vapi_url = 'https://{}/api'.format(self.args.server)

        # Create an authenticated stub configuration object that can be used to
        # issue requests against vCenter.
        session = requests.Session()
        if self.args.skipverification:
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

        # Create and Delete TagCategory to Verify connection is successful
        print('\nStep 3: Creating and Deleting Tag Category...\n')
        self.category_svc = Category(stub_config)

        self.category_id = self.create_tag_category('TestTagCat', 'TestTagDesc',
                                                    CategoryModel.Cardinality.MULTIPLE)
        assert self.category_id is not None
        print('Tag category created; Id: {0}\n'.format(self.category_id))

        # Delete TagCategory
        self.category_svc.delete(self.category_id)

        self.session.delete()
        print('VAPI session disconnected successfully...')

    def create_tag_category(self, name, description, cardinality):
        """create a category. User who invokes this needs create category privilege."""
        create_spec = self.category_svc.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.cardinality = cardinality
        associableTypes = set()
        create_spec.associable_types = associableTypes
        return self.category_svc.create(create_spec)


def main():
    embedded_psc_sso_workflow = EmbeddedPscSsoWorkflow()
    embedded_psc_sso_workflow.setup()
    embedded_psc_sso_workflow.run()


# Start program
if __name__ == '__main__':
    main()
