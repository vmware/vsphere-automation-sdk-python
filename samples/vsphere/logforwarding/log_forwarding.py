#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017, 2018. All Rights Reserved.
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


from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import vapiconnect
from tabulate import tabulate

from com.vmware.appliance.logging_client import Forwarding


class LogForwarding(object):
    """
    Demonstrates log forwarding API operations

    Prerequisites:
        - vCenter
        - Log host listening to syslog packets over any of the supported
          protocols UDP/TCP/TLS
    """

    def __init__(self):
        self.loghost = None
        self.protocol = None
        self.port = None
        self.stub_config = None
        self.log_forwarding_client = None

    def setup(self):
        parser = sample_cli.build_arg_parser()

        parser.add_argument('--loghost',
                            required=True,
                            action='store',
                            help='The log host')
        parser.add_argument('--port',
                            required=True,
                            action='store',
                            help='The log host port number')
        parser.add_argument('--protocol',
                            required=True,
                            action='store',
                            help='The log host protocol (TCP/UDP/TLS)')

        args = sample_util.process_cli_args(parser.parse_args())
        self.loghost = args.loghost
        self.protocol = args.protocol
        self.port = int(args.port)

        # Connect to vAPI services
        self.stub_config = vapiconnect.connect(
                                    host=args.server,
                                    user=args.username,
                                    pwd=args.password,
                                    skip_verification=args.skipverification)

        self.log_forwarding_client = Forwarding(self.stub_config)

    def run(self):
        # Set log forwarding configuration
        self.set_log_forwarding()

        # Get log forwarding configuration
        self.get_log_forwarding()

        # Test log forwarding configuration
        self.test_log_forwarding()

        # Update log forwarding configuration
        self.update_log_forwarding()

    def set_log_forwarding(self):
        log_forwarding_config = [Forwarding.Config(hostname=self.loghost,
                                                   port=self.port,
                                                   protocol=self.protocol)]
        self.log_forwarding_client.set(log_forwarding_config)

    def get_log_forwarding(self):
        configs = self.log_forwarding_client.get()

        print("\nLog forwarding configurations:")
        table = [[cfg.hostname, cfg.port, cfg.protocol] for cfg in configs]
        headers = ["Loghost", "Port", "Protocol"]
        print(tabulate(table, headers))

    def test_log_forwarding(self):
        test_response = self.log_forwarding_client.test(True)

        print("\nLog forwarding test response:")
        table = [[resp.hostname,
                  resp.state,
                  resp.message.default_message if resp.message else None]
                 for resp in test_response]
        headers = ["Loghost", "State", "Message"]
        print(tabulate(table, headers))

    def update_log_forwarding(self):
        # Read log forwarding configuration
        log_forwarding_config = self.log_forwarding_client.get()

        # Delete the newly added configuration
        log_forwarding_config = list(filter(
                                    lambda cfg: cfg.hostname != self.loghost,
                                    log_forwarding_config))

        # Apply the modified log forwarding configuration
        self.log_forwarding_client.set(log_forwarding_config)


def main():
    log_forwarding = LogForwarding()
    log_forwarding.setup()
    log_forwarding.run()

if __name__ == '__main__':
    main()
