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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.7+'

import argparse
from tabulate import tabulate
from samples.vsphere.common import vapiconnect
from com.vmware.appliance.recovery.backup_client import Job


class BackupJob(object):
    """
    Demonstrates backup job operations

    Retrieves backup job details from vCenter and prints the data in
    tabular format

    Prerequisites:
        - vCenter
        - Backup operation is performed on the vCenter either manually or
          by scheduled backups
    """

    def __init__(self):
        self.stub_config = None

    def setup(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('--server',
                            required=True,
                            action='store',
                            help='FQDN of the VCSA')

        parser.add_argument('--server-user',
                            required=True,
                            action='store',
                            help='Username for the VCSA')

        parser.add_argument('--server-password',
                            required=True,
                            action='store',
                            help='Password for the VCSA')

        parser.add_argument('-v', '--skipverification',
                            required=False,
                            action='store_true',
                            help='Skip SSL Verification')

        parser.add_argument('--location',
                            required=False,
                            action='store',
                            help='URL of the backup location')

        parser.add_argument('--location-user',
                            required=False,
                            action='store',
                            help='Username for the given location')

        parser.add_argument('--location-password',
                            required=False,
                            action='store',
                            help='Password for the given location')

        parser.add_argument('--backup-password',
                            required=False,
                            action='store',
                            help='Password for the backup')

        parser.add_argument('--backup-comment',
                            required=False,
                            action='store',
                            help='Comment for the backup')

        parser.add_argument('-lb', '--list-backup',
                    required=False,
                    action='store_true',
                    help='Switch to list backup jobs')

        parser.add_argument('-gb', '--get-backup',
                    required=False,
                    action='store',
                    help='Backup Job ID to Get Information About')

        parser.add_argument('-nb', '--create-backup',
                    required=False,
                    action='store_true',
                    help='Switch to create backup job')                    

        parser.add_argument('-cb', '--cancel-backup',
                    required=False,
                    action='store',
                    help='Backup Job ID to Cancel Job')

        args = parser.parse_args()

        self.server = args.server
        self.server_user = args.server_user
        self.server_password = args.server_password
        self.location = args.location
        self.location_user = args.location_user
        self.location_password = args.location_password
        self.backup_password = args.backup_password
        self.backup_comment = args.backup_comment
        self.list_backup = args.list_backup
        self.get_backup = args.get_backup
        self.create_backup = args.create_backup
        self.cancel_backup = args.cancel_backup

        # Connect to vAPI services
        self.stub_config = vapiconnect.connect(
                                    host=self.server,
                                    user=self.server_user,
                                    pwd=self.server_password,
                                    skip_verification="TRUE")

        self.job_client = Job(self.stub_config)

    def list_backup_job(self):
        job_list = self.job_client.list()
        self.print_output(job_list) 

    def get_backup_job(self):
        self.print_output(self.get_backup)

    def create_backup_job(self):
        backup_type = (self.location.split(':')[0]).upper()
        piece = self.job_client.BackupRequest(
                                    parts = ["common"], 
                                    backup_password = self.backup_password, 
                                    location_type = backup_type, 
                                    location = self.location, 
                                    location_user = self.location_user, 
                                    location_password = self.location_password, 
                                    comment = self.backup_comment)
        
        job_create = self.job_client.create(piece)
        self.print_output(job_create.id) 


    def cancel_backup_job(self):
        job_cancel = self.job_client.cancel(self.cancel_backup)
        self.print_output(self.cancel_backup)   

    def print_output(self, job):
        table = []

        if type(job) is list: 
            for bkupjob in job:
                info = self.job_client.get(bkupjob)
                if info.end_time is None:
                    duration = None
                else: 
                    duration = info.end_time - info.start_time
                row = [info.id,
                    info.state.capitalize(),
                    info.start_time.strftime("%b %d %Y %H:%M"),
                    duration]
                table.append(row)
        else:
            info = self.job_client.get(job)
            if info.end_time is None:
                duration = None
            else: 
                duration = info.end_time - info.start_time
            row = [info.id,
                    info.state.capitalize(),
                    info.start_time.strftime("%b %d %Y %H:%M"),
                    duration]
            table.append(row)

        headers = ["ID", "Status", "Start time", "Duration"]
        print(tabulate(table, headers))

def main():
    backup_job = BackupJob()
    backup_job.setup()
    if backup_job.list_backup:
        backup_job.list_backup_job()
    if backup_job.get_backup:
        backup_job.get_backup_job()
    if backup_job.create_backup:
        backup_job.create_backup_job()
    if backup_job.cancel_backup:
        backup_job.cancel_backup_job()

if __name__ == '__main__':
    main()