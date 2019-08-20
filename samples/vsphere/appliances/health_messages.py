#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
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
__vcenter_version__ = '6.7+'

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import (sample_cli, sample_util)
from samples.vsphere.common.ssl_helper import get_unverified_session


class HealthMessages(object):
    """
    Demonstrates getting Health messages for memory, storage and cpu

    Retrieves Health messages details from vCenter and prints the data

    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()

        parser.add_argument(
            '--item',
            required=True,
            action='store',
            choices=['memory', 'cpu', 'storage'],
            help='Specify the name of health item to view the messages')

        args = sample_util.process_cli_args(parser.parse_args())
        self.item = args.item
        # Connect to vAPI services
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        message_list = self.client.appliance.Health.messages(self.item)
        print("Health Alarams")
        print("-------------------\n")
        if not message_list:
            print("No health alarms for : " + self.item)
        else:
            for message in message_list:
                print("Alert time : {}".format(message.time))
                print("Alert message Id: " + message.id)
                local_message = message.message
                default_msg = local_message.default_message
                print("Alert message : " + default_msg)


def main():
    health_sample = HealthMessages()
    health_sample.run()


if __name__ == '__main__':
    main()
