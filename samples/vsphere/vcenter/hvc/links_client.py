#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2018. All Rights Reserved.
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
__vcenter_version__ = '6.6.1'

import argparse

from com.vmware.vcenter.hvc_client import Links

from samples.vsphere.common import vapiconnect


class LinksClient(object):
    """
    Description: Demonstrates link Create, List, Delete operations with a
    foreign platform service controller (PSC) on a different SSO domain.
    - Step 1: Create a link with a foreign domain.
    - Step 2: List all the linked domains.
    - Step 3: Delete the existing link with the foreign domain.

    Sample Prerequisites:
    - The sample needs a second vCenter on a different SSO domain.
    - The user invoking the API should have the HLM.Manage privilege.
    """

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-s', '--server',
                            required=True,
                            help='vSphere service IP to connect to')

        parser.add_argument('-u', '--username',
                            required=True,
                            help='Username to use when connecting to vc')

        parser.add_argument('-p', '--password',
                            required=True,
                            help='Password to use when connecting to vc')

        parser.add_argument('--foreignhost',
                            required=True,
                            help='FOREIGN PSC HOSTNAME.')

        parser.add_argument('--foreignusername',
                            required=True,
                            help='Administrator username for the foreign domain. '
                                 'Eg - Administrator')

        parser.add_argument('--foreignpassword',
                            required=True,
                            help='Administrator password for the foreign domain.')

        parser.add_argument('--foreigndomain',
                            required=True,
                            help='SSO Domain name for the foreign PSC. Eg - vsphere.local')

        parser.add_argument('--foreignport',
                            required=False,
                            default='443',
                            help='SSO Domain name for the foreign PSC. Eg - vsphere.local')

        parser.add_argument('-v', '--skipverification',
                            action='store_true',
                            help='OPTIONAL: Foreign HTTPS Port. Default: 443')

        parser.add_argument('-c', '--cleardata',
                            action='store_true',
                            help='Clean up after sample run')

        args = parser.parse_args()

        # Login to vCenter
        stub_config = vapiconnect.connect(host=args.server,
                                          user=args.username,
                                          pwd=args.password)

        # Create links stub
        self.links_client = Links(stub_config)

        self.foreignhost = args.foreignhost
        self.foreignusername = args.foreignusername
        self.foreignpassword = args.foreignpassword
        self.foreigndomain = args.foreigndomain
        self.foreignport = args.foreignport
        self.cleanup = args.cleardata
        self.linked_domain_id = None

    def create_link(self):
        link_spec = self.links_client.CreateSpec(psc_hostname=self.foreignhost,
                                                 domain_name=self.foreigndomain,
                                                 username=self.foreignusername,
                                                 password=self.foreignpassword,
                                                 port=self.foreignport)

        self.linked_domain_id = self.links_client.create(link_spec)
        print('Link successful. Link ID - {}'.format(self.linked_domain_id))

    def list_linked_domains(self):
        print('Getting all the links.')
        links = self.links_client.list()
        for link in links:
            print('Link ID: {}'.format(link))

    def unlink(self):
        if self.cleanup:
            self.links_client.delete(self.linked_domain_id)
            print('Link ({}) deleted successful.'.format(self.linked_domain_id))


def main():
    links_client = LinksClient()
    links_client.create_link()
    links_client.list_linked_domains()
    links_client.unlink()


if __name__ == '__main__':
    main()
