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

from vmware.vapi.vmc.client import create_vmc_client

from samples.vmc.helpers.sample_cli import parser


class VmcSiteRecoveryInfo(object):
    """
    Retrieves details of site recovery from the
    VMware Cloud Disaster Recovery As a Service (VMC DRaaS)

    Sample Prerequisites:
        - Site Recovery Add-on should be activated in the SDDC
        - An organization associated with the calling user.
        - A SDDC in the organization with SRM Addon activated.
        - Refresh Token
    """
    def __init__(self):
        args = parser.parse_args()
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.client = create_vmc_client(refresh_token=args.refresh_token)

    def get_draas_info(self):
        dr_status = self.client.draas.SiteRecovery.get(self.org_id, self.sddc_id)
        print("Vmware Cloud Site Recovery Status {}".
              format(dr_status.site_recovery_state))
        print("Vmware Cloud DRaaS H5 URL {}".format(dr_status.draas_h5_url))
        print("*** Vmware Cloud DRaaS Srm Node Details ***")
        srm_nodes_list = dr_status.srm_nodes
        for node in srm_nodes_list:
            print("\nSRM Node Id {} , status {}".format(node.id, node.state))
            print("SRM IP Address {}".format(node.ip_address))
            print("SRM IP Address {}".format(node.hostname))

        print("\n*** Vmware Cloud DRaaS vSphere Replication (VR) Node Details ***")
        print("VSphere Replication (VR) Node Status: {} , Id: {}"
              .format(dr_status.vr_node.state, dr_status.vr_node.id))
        print("VR IP address {}".format(dr_status.vr_node.ip_address))
        print("VR HostName {}".format(dr_status.vr_node.hostname))


def main():
    vmc_site_recovery_info = VmcSiteRecoveryInfo()
    vmc_site_recovery_info.get_draas_info()


if __name__ == '__main__':
    main()
