"""
* *******************************************************
* Copyright VMware, Inc. 2013, 2016. All Rights Reserved.
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

import argparse
import traceback
from samples.vsphere.common.service_manager_factory import ServiceManagerFactory


class SampleBase(object):
    def __init__(self, description):
        if description is None:
            raise Exception('Sample description cannot be empty')
        self.description = description
        # setup the argument parser
        self.argparser = argparse.ArgumentParser(description=description)
        self.argparser.add_argument('-s', '--server',
                                    help='Hostname of vCenter Server')
        self.argparser.add_argument('-u', '--username',
                                    help='Username to login to the vCenter Server')
        self.argparser.add_argument('-p', '--password',
                                    help='Password to login to the vCenter Server')
        self.argparser.add_argument('-c', '--cleardata', action='store_true',
                                    help='Clears the sample data on server after running')
        self.argparser.add_argument('-v', '--skipverification',
                                    action='store_true',
                                    help='Do not verify server certificate')
        self.args = None
        self.server = None
        self.username = None
        self.password = None
        self.cleardata = False
        self.skip_verification = False

    def parse_args(self):
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name == '_options':
                attr()  # calling the method
        self.args = self.argparser.parse_args()  # parse all the sample arguments when they are all set

        self.server = self.args.server
        assert self.server is not None
        print('server: {0}'.format(self.server))

        self.username = self.args.username
        assert self.username is not None

        self.password = self.args.password
        assert self.password is not None

        self.cleardata = self.args.cleardata
        self.skip_verification = self.args.skipverification

    def before(self):

        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name == '_setup':
                attr()  # calling the method

    def run(self):
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name == '_execute':
                try:
                    attr()  # calling the method
                except Exception as e:
                    # print the exception and move on to the cleanup stage if cleardata is set to True.
                    traceback.print_exc()
                    if bool(self.cleardata) is not True:
                        # re-throw the exception
                        raise Exception(e)

    def after(self):
        if bool(self.cleardata) is True:
            for name in dir(self):
                attr = getattr(self, name)
                if callable(attr) and name == '_cleanup':
                    attr()  # calling the method

    def main(self):
        self.parse_args()
        self.before()
        self.run()
        self.after()

    def get_service_manager(self):
        return ServiceManagerFactory.get_service_manager(self.server,
                                                         self.username,
                                                         self.password,
                                                         self.skip_verification)
