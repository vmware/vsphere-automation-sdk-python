"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
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

from six.moves import cStringIO
from vmware.vapi.bindings.struct import PrettyPrinter

from samples.vsphere.common import sample_cli
from samples.vsphere.vcenter.setup import testbed


def pp(value):
    """ Utility method used to print the data nicely. """
    output = cStringIO()
    PrettyPrinter(stream=output).pprint(value)
    return output.getvalue()


def parse_cli_args():
    """
    Parse the server IP and credential used by samples.
    Use values from command line arguments if present, otherwise use values
    from testbed.py
    """
    # parse command line
    parser = sample_cli.build_arg_parser()
    args = parser.parse_args()
    return process_cli_args(args)


def parse_cli_args_vm(vm_name):
    """
    Parse the server IP, credential and vm name used by vcenter vm samples.
    Use values from command line arguments if present, otherwise use values
    from testbed.py
    """
    # parse command line
    parser = sample_cli.build_arg_parser()
    parser.add_argument('-n', '--vm_name',
                        action='store',
                        help='Name of the testing vm')
    args = parser.parse_args()

    server, username, password, cleardata, skip_verification = \
        process_cli_args(args)

    if args.vm_name:
        vm_name = args.vm_name
    else:
        print("Try to use vm name({}) specified in testbed.py".format(vm_name))
    if not vm_name:
        raise Exception("vm name is required")
    print("vm name = {}".format(vm_name))

    return server, username, password, cleardata, skip_verification, vm_name


def process_cli_args(args):
    """
    Process server IP and credential args.
    """

    if args.server:
        server = args.server
    else:
        print("Using vcenter server specified in testbed.py")
        server = testbed.config['SERVER']
    if not server:
        raise Exception("vcenter server is required")
    print("vcenter server = {}".format(server))

    if args.username:
        username = args.username
    else:
        print("Using vc user specified in testbed.py")
        username = testbed.config['USERNAME']
    if not username:
        raise Exception("vc username is required")
    print("vc username = {}".format(username))

    if args.password:
        password = args.password
    else:
        print("Using vc password specified in testbed.py")
        password = testbed.config['PASSWORD']

    cleardata = args.cleanup
    print("sample cleanup = {}".format(cleardata))

    skip_verification = args.skipverification
    print("skip server cert verification = {}".format(skip_verification))

    return server, username, password, cleardata, skip_verification


class Context(object):
    """Class that holds common context for running vcenter samples."""

    def __init__(self, testbed, service_instance, stub_config):
        # Testbed configuration
        self.testbed = testbed

        # pyVmomi SOAP Service Instance
        self.service_instance = service_instance

        # vAPI stub configuration used to make other stubs
        self.stub_config = stub_config

        self.option = {}

    @property
    def testbed(self):
        return self._testbed

    @testbed.setter
    def testbed(self, value):
        self._testbed = value

    @property
    def service_instance(self):
        return self._service_instance

    @service_instance.setter
    def service_instance(self, value):
        self._service_instance = value

    @property
    def soap_stub(self):
        return self._service_instance._stub

    @soap_stub.setter
    def soap_stub(self, value):
        self._soap_stub = value

    @property
    def stub_config(self):
        return self._stub_config

    @stub_config.setter
    def stub_config(self, value):
        self._stub_config = value

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, value):
        self._option = value

    def to_option_string(self):
        s = ['=' * 79,
             'Testbed Options:',
             '=' * 79]
        s += ['   {}: {}'.format(k, self._option[k])
              for k in sorted(self._option.keys())]
        s += ['=' * 79]
        return '\n'.join(s)
