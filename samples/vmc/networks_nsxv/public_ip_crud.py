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

from samples.vmc.helpers.sample_cli import parser, optional_args
from com.vmware.vmc.model_client import SddcAllocatePublicIpSpec
from vmware.vapi.vmc.client import create_vmc_client

from samples.vmc.helpers.vmc_task_helper import wait_for_task


class PublicIPsCrud(object):
    """
    Demonstrates public IP CRUD operations

    Sample Prerequisites:
        - An organization associated with the calling user.
        - A SDDC in the organization
    """

    def __init__(self):
        optional_args.add_argument(
            '--notes',
            default='Sample public IP',
            help='Notes of the new public IP')

        optional_args.add_argument(
            '--cleardata',
            action='store_true',
            help='Clean up after sample run')
        args = parser.parse_args()

        self.ip_id = None
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.notes = args.notes
        self.cleanup = args.cleardata
        self.vmc_client = create_vmc_client(args.refresh_token)

    def setup(self):
        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(
                self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".format(
                self.sddc_id, self.org_id))

    def request_public_ip(self):

        print('\n# Example: Request a new IP for SDDC')
        ip_spec = SddcAllocatePublicIpSpec(names=[self.notes], count=1)
        task = self.vmc_client.orgs.sddcs.Publicips.create(
            org=self.org_id, sddc=self.sddc_id, spec=ip_spec)

        wait_for_task(
            task_client=self.vmc_client.orgs.Tasks,
            org_id=self.org_id,
            task_id=task.id,
            interval_sec=2)

        ips = self.vmc_client.orgs.sddcs.Publicips.list(
            org=self.org_id, sddc=self.sddc_id)

        for ip in ips:
            if ip.name == self.notes:
                self.ip_id = ip.allocation_id
                print('# Successfully requested public IP {}'.format(
                    ip.public_ip))
                break
        else:
            raise Exception("Can't find public IP with notes {}".format(
                self.notes))

    def get_public_ip(self):

        print('\n# Example: List all public IPs for the SDDC')
        ips = self.vmc_client.orgs.sddcs.Publicips.list(
            org=self.org_id, sddc=self.sddc_id)
        self.print_output(ips)

        print('\n# Example: Get the specific IP with ID {}'.format(self.ip_id))
        ip = self.vmc_client.orgs.sddcs.Publicips.get(
            org=self.org_id, sddc=self.sddc_id, id=self.ip_id)
        self.print_output([ip])

    def update_public_ip(self):

        print('\n# Example: Update the public IP notes')
        ip = self.vmc_client.orgs.sddcs.Publicips.get(
            org=self.org_id, sddc=self.sddc_id, id=self.ip_id)
        ip.name = 'Updated ' + ip.name

        self.vmc_client.orgs.sddcs.Publicips.update(
            org=self.org_id,
            sddc=self.sddc_id,
            id=self.ip_id,
            action='rename',
            sddc_public_ip_object=ip)

        ip = self.vmc_client.orgs.sddcs.Publicips.get(
            org=self.org_id, sddc=self.sddc_id, id=self.ip_id)

        print('# List the updated public IP')
        self.print_output([ip])

    def delete_public_ip(self):
        if self.cleanup:
            self.vmc_client.orgs.sddcs.Publicips.delete(
                org=self.org_id, sddc=self.sddc_id, id=self.ip_id)
            print('\n# Example: Public IP "{}" is deleted'.format(self.notes))

    def print_output(self, ips):
        for ip in ips:
            print('Public IP: {}, ID: {}, Notes: {}'.format(
                ip.public_ip, ip.allocation_id, ip.name))


def main():
    public_ips_crud = PublicIPsCrud()
    public_ips_crud.setup()
    public_ips_crud.request_public_ip()
    public_ips_crud.get_public_ip()
    public_ips_crud.update_public_ip()
    public_ips_crud.delete_public_ip()


if __name__ == '__main__':
    main()
