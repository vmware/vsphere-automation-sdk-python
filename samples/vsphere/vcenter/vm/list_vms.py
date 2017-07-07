#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

import atexit
import socket
import re
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common.sample_util import pp
from com.vmware.vcenter_client import VM
from samples.vsphere.common.sample_cli import build_arg_parser
from samples.vsphere.common.sample_util import process_cli_args

"""
Demonstrates getting list of VMs present in vCenter
Sample Prerequisites:
vCenter/ESX
"""

stub_config = None
cleardata = False


def setup(context=None):
    global stub_config, cleardata, cert_path
    parser = build_arg_parser()
    parser.add_argument('-cpath', '--cert_path',
                        action='store',
                        help='Verify vCenter Server certificate')
    args = parser.parse_args()

    server, username, password, cleardata, skip_verification = process_cli_args(args)

    # Check if either of skipverification or cert_path is passed as an argument
    cert_path = None
    if args.cert_path:
        if re.match('\d+[.]\d+[.]\d+[.]\d+', server):
            try:
                server = socket.gethostbyaddr(server)[0]
            except Exception as e:
                print("SERVER IS NOT REACHABLE {}".format(e))
        cert_path = args.cert_path
    if not skip_verification and not cert_path:
        raise Exception("skipverification or cert_path required")
    print("cert_path = {}".format(cert_path))

    # Connect to VAPI
    stub_config = vapiconnect.connect(server, username, password,
                                      skip_verification, cert_path=cert_path)
    atexit.register(vapiconnect.logout, stub_config)


def run():
    """
    List VMs present in server
    """
    vm_svc = VM(stub_config)
    list_of_vms = vm_svc.list()
    print("----------------------------")
    print("List Of VMs")
    print("----------------------------")
    for vm in list_of_vms:
        print('{}'.format(vm))
    print("----------------------------")


def main():
    setup()
    run()


if __name__ == '__main__':
    main()
