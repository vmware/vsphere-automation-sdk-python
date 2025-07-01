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

from com.vmware.vapi.std.errors_client import InvalidRequest
from com.vmware.vmc.draas.model_client import ErrorResponse
from vmware.vapi.vmc.client import create_vmc_client

from samples.vmc.draas.helpers.draas_task_helper import wait_for_task
from samples.vmc.helpers.sample_cli import parser, optional_args


class SiteRecoveryActivationOperations(object):
    """
    Demonstrates VMware Cloud Disaster Recovery As a Service (DRaaS)
    Site Recovery Activation Operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization.
        - Refresh Token
    """

    def __init__(self):
        optional_args.add_argument('-c', '--cleardata',
                                   action='store_true',
                                   help='Clean up after sample run')

        optional_args.add_argument('--interval_sec',
                                   default=60,
                                   help='Task pulling interval in sec')

        args = parser.parse_args()
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.interval_sec = int(args.interval_sec)

        self.cleanup = args.cleardata
        self.vmc_client = create_vmc_client(refresh_token=args.refresh_token)

    def setup(self):
        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".
                             format(self.sddc_id, self.org_id))

    # Activate Site Recovery in a SDDC
    def activate_srm(self):
        try:
            srm_activation_task = self.vmc_client.draas.SiteRecovery.post(self.org_id,
                                                                          self.sddc_id)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(task_client=self.vmc_client.draas.Task,
                      org_id=self.org_id,
                      task_id=srm_activation_task.id,
                      interval_sec=self.interval_sec)

    # De-activate Site Recovery Instance in a SDDC. This is a forceful operation as force=True
    def deactivate_srm(self):
        if self.cleanup:
            try:
                srm_deactivation_task = self.vmc_client.draas.SiteRecovery.delete(self.org_id,
                                                                                  self.sddc_id,
                                                                                  force=True)
            except InvalidRequest as e:
                # Convert InvalidRequest to ErrorResponse to get error message
                error_response = e.data.convert_to(ErrorResponse)
                raise Exception(error_response.error_messages)

            wait_for_task(task_client=self.vmc_client.draas.Task,
                          org_id=self.org_id,
                          task_id=srm_deactivation_task.id,
                          interval_sec=self.interval_sec)


def main():
    srm_activation_ops = SiteRecoveryActivationOperations()
    srm_activation_ops.setup()
    srm_activation_ops.activate_srm()
    srm_activation_ops.deactivate_srm()


if __name__ == '__main__':
    main()
