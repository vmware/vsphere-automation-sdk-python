#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016, 2018. All Rights Reserved.
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
__copyright__ = 'Copyright 2018 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.7+'

from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.common.ssl_helper import get_unverified_session

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util


class ListServices(object):
    """
    Demonstrates the details of vCenter Services

    Retrieves the vCenter Services,  its Health Status and Service Startup Type.

    Prerequisites:
        - vCenter Server
    """

    def __init__(self):
        # Create argument parser for standard inputs:
        # server, username, password and skipverification
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Skip server cert verification if needed.
        # This is not recommended in production code.
        session = get_unverified_session() if args.skipverification else None

        # Connect to vSphere client
        self.client = create_vsphere_client(
            server=args.server,
            username=args.username,
            password=args.password,
            session=session)

    def run(self):
        services_list = self.client.vcenter.services.Service.list_details()
        for key, value in services_list.items():
            print(
                'Service Name: {}, Service Name Key: {}, Service Health: {}, Service Status: {}, Service Startup Type: {}'
            ).format(key, value.name_key, value.health, value.state,
                     value.startup_type)


def main():
    list_services = ListServices()
    list_services.run()


if __name__ == '__main__':
    main()
