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
__vcenter_version__ = '6.0+'

from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.cis.tagging_client import (Category, CategoryModel)

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import sso
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.ssl_helper import get_unverified_session


class EmbeddedPscSsoWorkflow(object):
    """
    Demonstrates how to Login to vCenter vAPI service with
    embedded Platform Services Controller.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        self.args = sample_util.process_cli_args(parser.parse_args())

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'embedded Platform Services Controller')

        # Since the platform services controller is embedded, the sso server
        # is the same as the vCenter server.
        sso_url = 'https://{}/sts/STSService'.format(self.args.server)

        print('\nStep 1: Connect to the Single Sign-On URL and '
              'retrieve the SAML bearer token.')

        authenticator = sso.SsoAuthenticator(sso_url)
        context = None
        if self.args.skipverification:
            context = get_unverified_context()
        bearer_token = authenticator.get_bearer_saml_assertion(
            self.args.username,
            self.args.password,
            delegatable=True,
            ssl_context=context)

        session = get_unverified_session() if self.args.skipverification else None

        # Connect to vSphere client
        client = create_vsphere_client(server=self.args.server,
                                       bearer_token=bearer_token,
                                       session=session)

        # Create and Delete TagCategory to Verify connection is successful
        print('\nStep 3: Creating and Deleting Tag Category...\n')
        create_spec = client.tagging.Category.CreateSpec()
        create_spec.name = 'TestTag_embeded_psc_sso_workflow'
        create_spec.description = 'TestTagDesc'
        create_spec.cardinality = CategoryModel.Cardinality.MULTIPLE
        create_spec.associable_types = set()
        category_id = client.tagging.Category.create(create_spec)
        assert category_id is not None
        print('Tag category created; Id: {0}\n'.format(category_id))

        # Delete TagCategory
        client.tagging.Category.delete(category_id)


def main():
    embedded_psc_sso_workflow = EmbeddedPscSsoWorkflow()
    embedded_psc_sso_workflow.run()


# Start program
if __name__ == '__main__':
    main()
