"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013, 2016. All Rights Reserved.
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

from vmware.vapi.security.sso import create_saml_bearer_security_context
from samples.vsphere.common import sso
from samples.vsphere.common.lookup_service_helper import LookupServiceHelper

from samples.vsphere.common.ssl_helper import get_unverified_context


class PlatformServiceController(object):
    """
    Manages services on the infrastructure node (e.g. lookup service, SSO etc.)
    """

    def __init__(self, lswsdlurl, lssoapurl, ssousername, ssopassword,
                 skip_verification):
        self.lswsdlurl = lswsdlurl
        self.lssoapurl = lssoapurl
        self.ssousername = ssousername
        self.ssopassword = ssopassword
        self.lookupservicehelper = None
        self.stsurl = None
        self.bearer_token = None  # SAML bearer token
        self.sec_ctx = None  # Security context
        self.skip_verification = skip_verification

    def login(self):
        """
        Finds the SSO URL from the lookup service and retrieves the SAML token from STS URL
        """
        print('Connecting to lookup service url: {0}'.format(self.lssoapurl))
        self.lookupservicehelper = LookupServiceHelper(wsdl_url=self.lswsdlurl,
                                                       soap_url=self.lssoapurl,
                                                       skip_verification=self.skip_verification)
        self.lookupservicehelper.connect()

        self.stsurl = self.lookupservicehelper.find_sso_url()
        assert self.stsurl is not None

        print('Retrieving a SAML bearer token from STS url : {0}'.format(
            self.stsurl))
        au = sso.SsoAuthenticator(self.stsurl)
        context = None
        if self.skip_verification:
            context = get_unverified_context()
        self.bearer_token = au.get_bearer_saml_assertion(
            self.ssousername, self.ssopassword, delegatable=True,
            ssl_context=context)
        self.sec_ctx = create_saml_bearer_security_context(self.bearer_token)
