"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
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

from six.moves import cStringIO
from vmware.vapi.bindings.struct import PrettyPrinter

from samples.vsphere.common import sample_cli
from samples.vsphere.vcenter.setup import testbed


def pp(value):
    """ Utility method used to print the data nicely. """
    output = cStringIO()
    PrettyPrinter(stream=output).pprint(value)
    return output.getvalue()


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
    args = process_cli_args(parser.parse_args())

    if args.vm_name:
        vm_name = args.vm_name
    else:
        print("Try to use vm name({}) specified in testbed.py".format(vm_name))
    if not vm_name:
        raise Exception("vm name is required")
    print("vm name = {}".format(vm_name))

    return args.server, args.username, args.password, args.cleardata, \
           args.skipverification, vm_name


def process_cli_args(args):
    """
    Verify if required inputs (server, username and password) are provided.
    If they are not passed through cmd arguments, we will try to get them from
    testbed.py. If they are not configured in testbed.py either, we will raise
    an exception to remind the user to provide them.
    """

    if not args.server:
        print("Using vcenter server specified in testbed.py")
        args.server = testbed.config['SERVER']
    if not args.server:
        raise Exception("vcenter server is required")
    print("vcenter server = {}".format(args.server))

    if not args.username:
        print("Using vc user specified in testbed.py")
        args.username = testbed.config['USERNAME']
    if not args.username:
        raise Exception("vc username is required")
    print("vc username = {}".format(args.username))

    if not args.password:
        print("Using vc password specified in testbed.py")
        args.password = testbed.config['PASSWORD']

    return args


class Context(object):
    """Class that holds common context for running vcenter samples."""

    def __init__(self, testbed, service_instance, client):
        # Testbed configuration
        self._testbed = testbed

        # pyVmomi SOAP Service Instance
        self._service_instance = service_instance

        # vAPI vSphere client
        self._client = client

        self._option = {}

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
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

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
