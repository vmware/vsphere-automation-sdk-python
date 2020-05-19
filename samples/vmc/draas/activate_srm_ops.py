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

import time
from samples.vmc.helpers.sample_cli import parser, optional_args

from vmware.vapi.vmc.client import create_vmc_client


class SrmActivationOperations(object):
    """
    Demonstrates VMware Cloud Disaster Recovery As a Service (DRaaS)
    Site Recovery Manager (SRM) Activation Operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization with SRM Addon activated.
        - Refresh Token
    """

    def __init__(self):
        optional_args.add_argument('-c', '--cleardata',
                                   action='store_true',
                                   help='Clean up after sample run')

        args = parser.parse_args()
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.query_wait_time = 100
        self.max_wait_time = 900

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

    # Activate SRM Addon in a SDDC
    def activate_srm(self):
        if self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id).site_recovery_state != "ACTIVATED":
            srm_activation = self.vmc_client.draas.SiteRecovery.post(self.org_id,
                                                                 self.sddc_id,
                                                                 activate_site_recovery_config=None)
            print("Activation of SRM {} : {}".format(srm_activation.status,
                                                     srm_activation.start_time))
            self.query_activation_status()
        else:
            print("SRM already activated in {}".format(self.sddc_id))

    '''
     Note: There is no Task API to query activation status, though there is a task structure
     Hence querying the SRM activation status with resource_id & state for the status.
    '''
    def query_activation_status(self):
        timeout = time.time() + self.max_wait_time
        while time.time() < timeout:
            time.sleep(self.query_wait_time)
            status = self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id)
            if status.site_recovery_state in ['ACTIVATED', 'DEACTIVATED', 'CANCELLED', 'FAILED']:
                print("Site Recovery (DRaaS) Activation Status in {} : {}"
                      .format(status.updated, status.site_recovery_state))
                break
            else:
                print("Site Recovery (DRaaS) Activation Status in {} : {}"
                      .format(status.updated, status.site_recovery_state))
                continue
        else:
            raise Exception("Max time out reached {}".format(self.max_wait_time))

    # De-activate SRM Addon in a SDDC. This is a forceful operation as force=True
    def deactivate_srm(self):
        if self.cleanup:
            print("Deactivating SRM")
            self.vmc_client.draas.SiteRecovery.delete(self.org_id,
                                                  self.sddc_id,
                                                  force=True)
            self.query_activation_status()


def main():
    srm_activation_ops = SrmActivationOperations()
    srm_activation_ops.activate_srm()
    srm_activation_ops.deactivate_srm()


if __name__ == '__main__':
    main()
