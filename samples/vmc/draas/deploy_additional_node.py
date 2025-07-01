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
from com.vmware.vmc.draas.model_client import ProvisionSrmConfig


class DeployAdditionalNode(object):
    """
    Demonstrates VMware Cloud Disaster Recovery As a Service (DRaaS)
    Additional Site Recovery Manager (SRM) Node Deployment operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization with SRM Addon activated
    """

    def __init__(self):
        optional_args.add_argument('-c', '--cleardata',
                                   action='store_true',
                                   help='Clean up after sample run')

        args = parser.parse_args()
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.wait_time = 100
        self.max_wait_time = 900
        self.node_extension_id = 'com.vcDr1'

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

        # Check if the SRM Add-on is activated in VMC
        if "ACTIVATED" != self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id).site_recovery_state:
            raise ValueError("DRaaS is not activated in SDDC with ID {} & org with ID {}".
                             format(self.sddc_id, self.org_id))

    # Deploy Additional SRM Node
    def deploy_srm(self):
        deploy_srm = self.vmc_client.draas.SiteRecoverySrmNodes.post(
            self.org_id,
            self.sddc_id,
            ProvisionSrmConfig(srm_extension_key_suffix=self.node_extension_id))
        print('Srm Additional Node Deployment Started {}'.format(deploy_srm.start_time))
        return deploy_srm.resource_id

    '''
       Note: There is no Task API to query activation status, though there is a task structure.
       Hence querying the SRM activation status with resource_id and state for the status.
    '''
    def query_deployment(self, deployed_node_id):
        srm_node_details = self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id).srm_nodes
        for node_index in range(len(srm_node_details)):
            if deployed_node_id == srm_node_details[node_index].id:
                timeout = time.time() + self.max_wait_time
                while time.time() < timeout:
                    node_details = self.vmc_client.draas.SiteRecovery.get(self.org_id, self.sddc_id)
                    time.sleep(self.wait_time)
                    if node_details.srm_nodes[node_index].state in ['READY', 'DELETING', 'CANCELLED', 'FAILED']:
                        print("Site Recovery (DRaaS) Additonal Node Deployment Status {} : {}"
                              .format(node_details.updated,
                                      node_details.srm_nodes[node_index].state))
                        break
                    else:
                        print("Site Recovery (DRaaS) Additonal Node Deployment Status {} : {}"
                              .format(node_details.updated,
                                      node_details.srm_nodes[node_index].state))
                        continue
                else:
                    raise Exception("Max time out reached {}".format(self.max_wait_time))
            node_index += 1

    # Deleting the additional node if with --cleardata flag
    def delete_node(self, node_id):
        if self.cleanup:
            print("Removing the Additional Node")
            self.vmc_client.draas.SiteRecoverySrmNodes.delete(
                self.org_id,
                self.sddc_id,
                node_id)
            self.query_deployment(node_id)


def main():
    deploy_addtional_nodes = DeployAdditionalNode()
    deploy_addtional_nodes.setup()
    srm_node_id = deploy_addtional_nodes.deploy_srm()
    deploy_addtional_nodes.query_deployment(srm_node_id)
    deploy_addtional_nodes.delete_node(srm_node_id)


if __name__ == '__main__':
    main()
