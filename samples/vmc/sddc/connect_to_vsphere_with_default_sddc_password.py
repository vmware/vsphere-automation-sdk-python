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
__vcenter_version__ = 'VMware Cloud on AWS'


from com.vmware.vapi.std.errors_client import NotFound
from com.vmware.vmc.model_client import ErrorResponse
from six.moves.urllib import parse
from samples.vmc.helpers.sample_cli import parser
from vmware.vapi.vmc.client import create_vmc_client
from vmware.vapi.vsphere.client import create_vsphere_client


class ConnectTovSphereWithDefaultCredentials(object):
    """
    Demonstrates how to connect to a vSphere in a SDDC
    using the initial cloud admin credentials.

    Sample Prerequisites:
        - A SDDC in the org
        - A firewall rule to access the vSphere
    """

    def __init__(self):
        args = parser.parse_args()

        self.refresh_token = args.refresh_token
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id

    def run(self):

        # Connect to VMware Cloud on AWS
        vmc_client = create_vmc_client(self.refresh_token)
        print(
            '\n# Example: Successfully login to VMware Cloud on AWS instance')

        # Check if the organization exists
        orgs = vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(
                self.org_id))

        # Check if the SDDC exists
        try:
            sddc = vmc_client.orgs.Sddcs.get(self.org_id, self.sddc_id)
        except NotFound as e:
            error_response = e.data.convert_to(ErrorResponse)
            raise ValueError(error_response.error_messages)

        # Get VC hostname
        server = parse.urlparse(sddc.resource_config.vc_url).hostname

        # Connect to vSphere client using the initial cloud admin credentials.
        # Please use the new credentials to login after you reset the default one.
        vsphere_client = create_vsphere_client(
            server,
            username=sddc.resource_config.cloud_username,
            password=sddc.resource_config.cloud_password)
        print("\n# Example: Successfully connect to vCenter at '{}'".format(
            server))

        # List VMs in the vSphere instance
        vms = vsphere_client.vcenter.VM.list()

        print('\n# Example: List VMs in the vSphere')
        for vm_summary in vms:
            print('VM ID: {}, VM Name: {}'.format(vm_summary.vm,
                                                  vm_summary.name))


def main():
    connect_to_vsphere = ConnectTovSphereWithDefaultCredentials()
    connect_to_vsphere.run()


if __name__ == '__main__':
    main()
