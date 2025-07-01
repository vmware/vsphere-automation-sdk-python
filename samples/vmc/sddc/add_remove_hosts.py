#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
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

import atexit
import requests

from samples.vmc.helpers.sample_cli import parser, optional_args
from com.vmware.vmc.model_client import EsxConfig, ErrorResponse
from com.vmware.vapi.std.errors_client import InvalidRequest
from vmware.vapi.vmc.client import create_vmc_client

from samples.vmc.helpers.vmc_task_helper import wait_for_task


class AddRemoveHosts(object):
    """
    Demonstrates add and remove ESX hosts

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        self.sddc_id = None
        self.org_id = None
        self.vmc_client = None
        self.refresh_token = None
        self.interval_sec = None

    def options(self):
        optional_args.add_argument('--interval-sec',
                            default=60,
                            help='Task pulling interval in sec')

        args = parser.parse_args()

        self.refresh_token = args.refresh_token
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.interval_sec = int(args.interval_sec)

    def setup(self):

        # Login to VMware Cloud on AWS
        session = requests.Session()
        self.vmc_client = create_vmc_client(self.refresh_token, session)
        atexit.register(session.close)

        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".
                             format(self.sddc_id, self.org_id))

    def add_host(self):
        print('\n# Example: Add 1 ESX hosts to SDDC {}:'.format(self.sddc_id))
        esx_config = EsxConfig(num_hosts=1)

        try:
            task = self.vmc_client.orgs.sddcs.Esxs.create(org=self.org_id,
                                                          sddc=self.sddc_id,
                                                          esx_config=esx_config)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(task_client=self.vmc_client.orgs.Tasks,
                      org_id=self.org_id,
                      task_id=task.id,
                      interval_sec=self.interval_sec)

    def remove_host(self):
        print('\n# Example: Remove 1 ESX host from SDDC {}:'.
              format(self.sddc_id))
        esx_config = EsxConfig(num_hosts=1)

        try:
            task = self.vmc_client.orgs.sddcs.Esxs.create(org=self.org_id,
                                                          sddc=self.sddc_id,
                                                          esx_config=esx_config,
                                                          action='remove')
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(task_client=self.vmc_client.orgs.Tasks,
                      org_id=self.org_id,
                      task_id=task.id,
                      interval_sec=self.interval_sec)


def main():
    esx_operations = AddRemoveHosts()
    esx_operations.options()
    esx_operations.setup()
    esx_operations.add_host()
    esx_operations.remove_host()


if __name__ == '__main__':
    main()
