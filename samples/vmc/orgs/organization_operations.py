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

import requests
import argparse
import atexit

from vmware.vapi.vmc.client import create_vmc_client


class OperationsOnOrganizations(object):
    """
    Demonstrates operations on organizations and features

    Sample Prerequisites:
        - At least one org associated with the calling user.
    """

    def __init__(self):
        self.org = None
        self.feature = None
        self.vmc_client = None
        self.refresh_token = None

    def options(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        required_args = parser.add_argument_group(
            'required arguments')
        required_args.add_argument(
            '--refresh_token',
            required=True,
            help='VMware Cloud API refresh token')

        self.refresh_token = parser.parse_args().refresh_token

    def setup(self):
        # Login to VMware Cloud on AWS
        session = requests.Session()
        self.vmc_client = create_vmc_client(self.refresh_token, session)
        atexit.register(session.close)

    def list_orgs(self):
        orgs = self.vmc_client.Orgs.list()
        if not orgs:
            raise ValueError('The sample requires at least one org associated'
                             'with the calling user')
        print("\n# Example: List organizations")
        for org in orgs:
            print('ID: {}, Display Name: {}'.format(org.id, org.display_name))

        self.org = orgs[0]

    def get_org_detail(self):
        org = self.org
        print('\n# Example: List details of the first organization {}:'.format(
            org.id))

        print(
            'ID: {}, Display Name: {}, Name: {}, Created: {}, Updated: {}, Project State: {}'
            .format(org.id, org.display_name, org.name,
                    org.created.strftime('%m/%d/%Y'),
                    org.updated.strftime('%m/%d/%Y'), org.project_state))


def main():
    org_operations = OperationsOnOrganizations()
    org_operations.options()
    org_operations.setup()
    org_operations.list_orgs()
    org_operations.get_org_detail()


if __name__ == '__main__':
    main()
