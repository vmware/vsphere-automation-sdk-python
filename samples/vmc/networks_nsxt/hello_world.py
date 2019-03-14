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

import argparse
import pprint

from com.vmware.nsx_policy_client_for_vmc import (
    create_nsx_policy_client_for_vmc)


class AuthExample(object):
    """
    Demonstrates how to authenticate to VMC using the NSX-T SDK
    and perform a simple read operation.

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-r', '--refresh-token',
                            required=True,
                            help='VMware Cloud API refresh token')

        parser.add_argument('-o', '--org-id',
                            required=True,
                            help='Organization identifier.')

        parser.add_argument('-s', '--sddc-id',
                            required=True,
                            help='Sddc Identifier.')

        args = parser.parse_args()

        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.vmc_client = create_nsx_policy_client_for_vmc(
            args.refresh_token, args.org_id, args.sddc_id)

    def get_domains(self):
        print('\n# Get Domains: List network domains:')
        domains = self.vmc_client.infra.Domains.list()
        pprint.pprint(domains)


def main():
    auth_example = AuthExample()
    auth_example.get_domains()


if __name__ == '__main__':
    main()
