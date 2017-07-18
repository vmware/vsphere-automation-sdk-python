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

import atexit
from com.vmware.cis.tagging_client import (Category, CategoryModel)
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import process_cli_args
from samples.vsphere.common.sample_cli import build_arg_parser


class CertConnect(object):
    """
    Demonstrates how to Connect to vCenter vAPI service with
    with Valid Cert
    """

    def __init__(self):
        self.server = None
        self.username = None
        self.password = None
        self.stub_config = None
        self.cleardata = None
        self.skip_verification = False
        self.cert_path = None
        self.category_svc = None
        self.category_id = None

    def setup(self):
        parser = build_arg_parser()
        parser.add_argument('-cpath', '--cert_path',
                            action='store',
                            help='path to a CA_BUNDLE file or directory with certificates of trusted CAs')
        args = parser.parse_args()

        self.server, self.username, self.password, self.cleardata, self.skip_verification = \
            process_cli_args(args)

        if args.cert_path:
            self.cert_path = args.cert_path

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'Valid Cert Verification')
        # Connect to VAPI
        self.stub_config = vapiconnect.connect(self.server, self.username, self.password,
                                               self.skip_verification,
                                               cert_path=self.cert_path)
        atexit.register(vapiconnect.logout, self.stub_config)

        # Create and Delete TagCategory to Verify connection is successful
        print('\nStep 3: Creating and Deleting Tag Category...\n')
        self.category_svc = Category(self.stub_config)

        self.category_id = self.create_tag_category('TestTagCat', 'TestTagDesc',
                                                    CategoryModel.Cardinality.MULTIPLE)
        assert self.category_id is not None
        print('Tag category created; Id: {0}\n'.format(self.category_id))

        # Delete TagCategory
        self.category_svc.delete(self.category_id)

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
    connect_with_cert = CertConnect()
    connect_with_cert.setup()
    connect_with_cert.run()


# Start program
if __name__ == '__main__':
    main()
