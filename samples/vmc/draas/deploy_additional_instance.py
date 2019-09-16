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
from com.vmware.vmc.draas.model_client import ProvisionSrmConfig
from vmware.vapi.vmc.client import create_vmc_client

from samples.vmc.draas.helpers.draas_task_helper import wait_for_task
from samples.vmc.helpers.sample_cli import parser, optional_args


class DeployAdditionalInstance(object):
    """
    Demonstrates VMware Cloud Disaster Recovery As a Service (DRaaS)
    Additional Site Recovery instance deployment operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization with Site Recovery activated
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

        '''
         SRM extension key suffix.This must be fewer than 13 characters
         and can include alphanumeric characters, hyphen, or period,
         but cannot start or end with a sequence of hyphen, or period characters
        '''
        self.extension_key = 'TestNode'

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

        # Check if Site Recovery is activated in VMC
        if "ACTIVATED" != self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id).site_recovery_state:
            raise ValueError("DRaaS is not activated in SDDC with ID {} & org with ID {}".
                             format(self.sddc_id, self.org_id))

    # Deploy Additional Site Recovery Instance
    def deploy_srm(self):
        try:
            print("Deploying Additional Site Recovery Instance")
            deployment_task = self.vmc_client.draas.SiteRecoverySrmNodes.post(
                self.org_id,
                self.sddc_id,
                ProvisionSrmConfig(srm_extension_key_suffix=self.extension_key))
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        wait_for_task(task_client=self.vmc_client.draas.Task,
                      org_id=self.org_id,
                      task_id=deployment_task.id,
                      interval_sec=self.interval_sec)
        return deployment_task.resource_id

    # Deleting the additional Site Recovery instance, if with --cleardata flag
    def delete_node(self, node_id):
        if self.cleanup:
            print("\nRemoving Additional Site Recovery Instance")
            try:
                srm_deactivation_task = self.vmc_client.draas.SiteRecoverySrmNodes.delete(self.org_id,
                                                                                          self.sddc_id,
                                                                                          node_id)
            except InvalidRequest as e:
                # Convert InvalidRequest to ErrorResponse to get error message
                error_response = e.data.convert_to(ErrorResponse)
                raise Exception(error_response.error_messages)

            wait_for_task(task_client=self.vmc_client.draas.Task,
                          org_id=self.org_id,
                          task_id=srm_deactivation_task.id,
                          interval_sec=self.interval_sec)


def main():
    deploy_addtional_instance = DeployAdditionalInstance()
    deploy_addtional_instance.setup()
    node_id = deploy_addtional_instance.deploy_srm()
    deploy_addtional_instance.delete_node(node_id)


if __name__ == '__main__':
    main()
