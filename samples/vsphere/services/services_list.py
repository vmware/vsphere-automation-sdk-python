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

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2018 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.7+'

from tabulate import tabulate

from com.vmware.vcenter.services_client import Service
from samples.vsphere.common import vapiconnect
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util

class ListServices(object):
    """
    Demonstrates the details of vCenter Services

    Retrieves the vCenter Services,  its Health Status and Service Startup Type.

    Prerequisites:
        - vCenter Server
    """


    def  __init__(self):
        self.stub_config = None

    def setup(self):
        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Connect to vSphere client
        self.stub_config = vapiconnect.connect(host=args.server,
                                               user=args.username,
                                               pwd=args.password,
                                               skip_verification=args.skipverification)
    def run(self):
        services_client = Service(self.stub_config)
        services_list = services_client.list_details()

        table = []
        for key,value in services_list.items():
            row = [key,
                   value.name_key,
                   value.health,
                   value.state,
                   value.startup_type]
            table.append(row)
        headers = ["Service Name", "Service Name Key", "Service Health", "Service Status", "Service Startup Type"]
        print(tabulate(table,headers))



def main():
    list_services = ListServices()
    list_services.setup()
    list_services.run()

if __name__ == '__main__':
    main()