#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017-2019. All Rights Reserved.
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

import os
from random import randrange
import argparse

from com.vmware.vapi.std.errors_client import InvalidRequest
from com.vmware.vmc.model_client import AwsSddcConfig, ErrorResponse, AccountLinkSddcConfig, SddcConfig
from vmware.vapi.vmc.client import create_vmc_client
from samples.vmc.helpers.vmc_task_helper import wait_for_task


class CreateDeleteSDDC(object):
    """
    Demonstrates create and delete a SDDC

    Sample Prerequisites:
        - An organization associated with the calling user.
    """

    def __init__(self):
        parser = argparse.ArgumentParser()

        required_args = parser.add_argument_group(
            'required arguments')
        optional_args = parser.add_argument_group(
            'optional arguments')

        required_args.add_argument(
            '--refresh_token',
            required=True,
            help='Refresh token obtained from CSP')

        required_args.add_argument(
            '--org_id',
            required=True,
            help='Organization identifier.')

        optional_args.add_argument(
            '--sddc-name',
            help="Name of the SDDC to be created. "
            "Default is 'Sample SDDC xx'")

        optional_args.add_argument('--region', default='US_WEST_2', help='AWS Region')

        optional_args.add_argument(
            '--interval-sec',
            default=60,
            help='Task pulling interval in sec')

        optional_args.add_argument(
            '--listsddc',
            action='store_true',
            help='List SDDCs in the specified Org')

        optional_args.add_argument(
            '--createsddc',
            action='store_true',
            help='Create an SDDC in the specified Org')

        optional_args.add_argument(
            '--deletesddc',
            action='store_true',
            help='Deletes the SDDC in the specified Org ')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')

        args = parser.parse_args()

        self.refresh_token = args.refresh_token
        self.org_id = args.org_id
        self.region = args.region
        self.listsddc = args.listsddc
        self.createsddc = args.createsddc
        self.deletesddc = args.deletesddc
        self.cleanup = args.cleardata
        self.sddc_id = None
        self.sddc_name = args.sddc_name or 'Sample SDDC {}'.format(
            randrange(100))
        self.interval_sec = int(args.interval_sec)

        # Login to VMware Cloud on AWS
        self.vmc_client = create_vmc_client(self.refresh_token)

    def setup(self):

        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(
                self.org_id))

    def create_sddc(self):
        print('\n# Example: Create a SDDC ({}) in org {}:'.format(
            self.sddc_name, self.org_id))

        account_linking_config = None

        # Get connected accounts if any
        account_ids = self.vmc_client.orgs.account_link.ConnectedAccounts.get(
            self.org_id)

        if len(account_ids) > 0:
            account_id = account_ids[0].id

            vpc_map = self.vmc_client.orgs.account_link.CompatibleSubnets.get(
                org=self.org_id, linked_account_id=account_id).vpc_map

            customer_subnet_id = self.get_subnet_id(vpc_map)
            if not customer_subnet_id:
                raise ValueError('No available subnet for region {}'.format(
                    self.region))

            account_linking_config = AccountLinkSddcConfig(
                customer_subnet_ids=[customer_subnet_id],
                connected_account_id=account_id)

        sddc_config = AwsSddcConfig(
            region=self.region,
            name=self.sddc_name,
            account_link_sddc_config=[account_linking_config] if account_linking_config else None,
            provider=os.environ.get('VMC_PROVIDER', SddcConfig.PROVIDER_AWS),
            num_hosts=4,
            deployment_type=SddcConfig.DEPLOYMENT_TYPE_SINGLEAZ)

        try:
            task = self.vmc_client.orgs.Sddcs.create(
                org=self.org_id, sddc_config=sddc_config)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(
            task_client=self.vmc_client.orgs.Tasks,
            org_id=self.org_id,
            task_id=task.id,
            interval_sec=self.interval_sec)

        print('\n# Example: SDDC created:')
        self.sddc_id = task.resource_id
        sddc = self.vmc_client.orgs.Sddcs.get(self.org_id, self.sddc_id)
        self.print_output([sddc])

    def delete_sddc(self):
        # Get SDDC ID by name
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        for sddc in sddcs:
            if sddc.name == self.sddc_name:
                self.sddc_id = sddc.id
                break
        else:
            raise ValueError('Cannot find sddc "{}"'.format(sddc_name))

        print('\n# Example: Delete SDDC {} from org {}'.format(
            self.sddc_id, self.org_id))

        try:
            task = self.vmc_client.orgs.Sddcs.delete(
                org=self.org_id, sddc=self.sddc_id)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(
            task_client=self.vmc_client.orgs.Tasks,
            org_id=self.org_id,
            task_id=task.id,
            interval_sec=self.interval_sec)

        print('\n# Example: Remaining SDDCs:')
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        self.print_output(sddcs)

    def list_sddc(self):
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if not sddcs:
            raise ValueError('The sample requires at least one SDDC associated'
                             'with the calling user')
        print("\n# Example: List SDDCs")
        self.print_output(sddcs)

    def print_output(self, sddcs):
        for sddc in sddcs:
            print('ID: {}, Name: {}'.format(sddc.id, sddc.name))

    def get_subnet_id(self, vpc_map):
        for v in vpc_map.values():
            for subnet in v.subnets:
                if subnet.region_name.lower() == self.region.lower():
                    return subnet.subnet_id


def main():
    sddc_operations = CreateDeleteSDDC()
    sddc_operations.setup()
    if sddc_operations.listsddc:
        sddc_operations.list_sddc()
    if sddc_operations.createsddc:
        sddc_operations.create_sddc()
    if sddc_operations.deletesddc:
        sddc_operations.delete_sddc()
    if sddc_operations.cleanup:
        sddc_operations.delete_sddc()


if __name__ == '__main__':
    main()
