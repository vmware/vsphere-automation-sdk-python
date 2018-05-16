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
__vcenter_version__ = '6.6.1'

import argparse

from com.vmware.vcenter.hvc.management_client import Administrators
from com.vmware.vmc.model_client import *

from samples.vsphere.common import vapiconnect


class AdministratorClient(object):
    """
    Description: Demonstrates Add, Get, Remove operations for a given
    Identity Source group to the CloudAdminGroup.
    Step 1: Add the given group to CloudAdminGroup.
    Step 2: Get all the groups in CloudAdminGroup.
    Step 3: Remove the given group from CloudAdminGroup.

    Sample Prerequisites:
    - The sample needs an Identity source added to the vCenter apart from the
    - default ones already added during vCenter deployment.
    - The Identity source should contain one SSO group.
    - The user invoking the API should have the HLM.Manage privilege.
    -
    """

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-s', '--server',
                            required=True,
                            help='vSphere service IP to connect to')

        parser.add_argument('-u', '--username',
                            required=True,
                            help='Username to use when connecting to vc')

        parser.add_argument('-p', '--password',
                            required=True,
                            help='Password to use when connecting to vc')

        parser.add_argument('--groupname',
                            required=True,
                            help='Name of the new group to be added.')

        parser.add_argument('-v', '--skipverification',
                            action='store_true',
                            help='Verify server certificate when connecting to vc.')

        parser.add_argument('-c', '--cleardata',
                            action='store_true',
                            help='Clean up after sample run')

        args = parser.parse_args()

        # Login to vCenter
        stub_config = vapiconnect.connect(host=args.server,
                                          user=args.username,
                                          pwd=args.password)
        # Create admin stub
        self.admin_client = Administrators(stub_config)
        self.cleanup = args.cleardata
        self.groupname = args.groupname

    def add_cloud_admin_group(self):
        self.admin_client.add(self.groupname)
        print('Group {} added successful.'.format(self.groupname))

    def list_cloud_admin_group(self):
        print('Getting all the groups under CloudAdminGroup.')
        groups = self.admin_client.get()
        for group in groups:
            print('Group: {}'.format(group))

    def delete_cloud_admin_group(self):
        if self.cleanup:
            self.admin_client.remove(self.groupname)
            print('Group {} removed successful'.format(self.groupname))


def main():
    admin_client = AdministratorClient()
    admin_client.add_cloud_admin_group()
    admin_client.list_cloud_admin_group()
    admin_client.delete_cloud_admin_group()


if __name__ == '__main__':
    main()
