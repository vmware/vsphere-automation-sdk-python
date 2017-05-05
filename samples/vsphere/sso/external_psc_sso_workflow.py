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

import os
import argparse
import requests
from pprint import pprint

from six.moves.urllib import request, parse

from com.vmware.cis_client import Session

from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import create_saml_bearer_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from com.vmware.cis.tagging_client import (Category, CategoryModel)

from samples.vsphere.common import sso
from samples.vsphere.common.lookup_service_helper import LookupServiceHelper
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vapiconnect import create_unverified_session


class ExternalPscSsoWorkflow(object):
    """
    Demonstrates how to Login to vCenter vAPI service with
    external Platform Services Controller.
    """

    def __init__(self):
        self.lswsdl = None
        self.lsurl = None
        self.mgmtinstancename = None
        self.username = None
        self.password = None
        self.session = None
        self.session_id = None
        self.args = None
        self.argparser = None
        self.mgmtinstancename = None
        self.skip_verification = False
        self.category_svc = None
        self.category_id = None

    def options(self):
        self.argparser = argparse.ArgumentParser(description=self.__doc__)
        # setup the argument parser
        self.argparser.add_argument('-w', '--lswsdl',
                                    help='Path to the Lookup Service WSDL. '
                                         'By default, lookupservice.wsdl in '
                                         '../wsdl will be used if the parameter'
                                         ' is absent')
        self.argparser.add_argument('-s', '--lsurl', help='Lookup service URL')
        self.argparser.add_argument('-m', '--mgmtinstancename',
                                    help='Instance name of the vCenter Server '
                                         'management node. '
                                         'When only one node is registered, '
                                         'it is selected by default; otherwise,'
                                         ' omit the parameter to get a list of '
                                         'available nodes.')
        self.argparser.add_argument('-u', '--username', help='SSO user name')
        self.argparser.add_argument('-p', '--password',
                                    help='SSO user password')
        self.argparser.add_argument('-v', '--skipverification',
                                    action='store_true',
                                    help='Do not verify server certificate')
        self.args = self.argparser.parse_args()

    def setup(self):
        if self.args.lswsdl:
            self.lswsdl = os.path.abspath(self.args.lswsdl)
        else:
            self.lswsdl = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'wsdl',
                'lookupservice.wsdl')
        assert self.lswsdl is not None
        print('lswsdl: {0}'.format(self.lswsdl))

        self.lsurl = self.args.lsurl
        assert self.lsurl is not None
        print('lsurl: {0}'.format(self.lsurl))

        self.username = self.args.username
        assert self.username is not None

        self.password = self.args.password
        assert self.password is not None

        self.mgmtinstancename = self.args.mgmtinstancename
        self.skip_verification = self.args.skipverification

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'external Platform Services Controller')

        print('\nStep 1: Connect to the lookup service on the '
              'Platform Services Controller node: {0}'.format(self.lsurl))

        # Convert wsdl path to url
        self.lswsdl = parse.urljoin('file:', request.pathname2url(self.lswsdl))
        lookupservicehelper = LookupServiceHelper(wsdl_url=self.lswsdl,
                                                  soap_url=self.lsurl,
                                                  skip_verification=self.skip_verification)
        lookupservicehelper.connect()

        if self.mgmtinstancename is None:
            self.mgmtinstancename, self.mgmtnodeid = lookupservicehelper.get_default_mgmt_node()
        elif self.mgmtnodeid is None:
            self.mgmtnodeid = lookupservicehelper.get_mgmt_node_id(
                self.mgmtinstancename)
        assert self.mgmtnodeid is not None

        print('\nStep 2: Discover the Single Sign-On service URL'
              ' from lookup service.')
        sso_url = lookupservicehelper.find_sso_url()
        print('Sso URL: {0}'.format(sso_url))

        print('\nStep 3: Connect to the Single Sign-On URL and '
              'retrieve the SAML bearer token.')
        authenticator = sso.SsoAuthenticator(sso_url)
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

        print('\nStep 4. Discover the vAPI service URL from lookup service.')
        vapi_url = lookupservicehelper.find_vapi_url(self.mgmtnodeid)
        print('vAPI URL: {0}'.format(vapi_url))

        print('\nStep 5. Login to vAPI service using the SAML bearer token.')

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

        # Create and Delete TagCategory to Verify connection is successful
        print('\nStep 6: Creating and Deleting Tag Category...\n')
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

        self.session.delete()
        print('VAPI session disconnected successfully...')


def main():
    external_psc_sso_workflow = ExternalPscSsoWorkflow()
    external_psc_sso_workflow.options()
    external_psc_sso_workflow.setup()
    external_psc_sso_workflow.run()


# Start program
if __name__ == '__main__':
    main()
