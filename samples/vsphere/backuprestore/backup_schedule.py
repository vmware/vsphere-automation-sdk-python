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


from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import vapiconnect
from tabulate import tabulate

from com.vmware.appliance.recovery.backup_client import Schedules


class BackupSchedule(object):
    """
    Demonstrates backup schedule operations

    Prerequisites:
        - vCenter
        - Backup server (ftp/ftps/http/https/scp)
    """

    def __init__(self):
        self.stub_config = None

        # Scheudle backup to run on weekdays at 10:30 pm
        self.days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        self.hour = 22
        self.minute = 30

        # Retain last 30 backups
        self.max_count = 30

        self._schedule_id = 'test_schedule'


    def setup(self):
        parser = sample_cli.build_arg_parser()

        parser.add_argument('-location', '--location',
                            required=True,
                            action='store',
                            help='URL of the backup location')
        parser.add_argument('--location_user',
                            required=True,
                            action='store',
                            help='Username for the given location')
        parser.add_argument('--location_password',
                            required=True,
                            action='store',
                            help='Password for the given location')

        args = sample_util.process_cli_args(parser.parse_args())
        self.location = args.location
        self.location_user = args.location_user
        self.location_password = args.location_password

        # Connect to vAPI services
        self.stub_config = vapiconnect.connect(
                                    host=args.server,
                                    user=args.username,
                                    pwd=args.password,
                                    skip_verification=args.skipverification)

        self.schedule_client = Schedules(self.stub_config)

    def run(self):
        # Create a backup schedule
        self.create_schedule()

        # Update the backup schedule to take backup only on weekends
        self.days = ["SATURDAY", "SUNDAY"]
        self.update_schedule()

        # Get the updated backup schedule
        self.get_schedule()

        # Run backup operation using the scheduled configuration
        self.run_backup()

        # Delete the backup schedule
        self.delete_schedule()

    def create_schedule(self):
        retention_info = Schedules.RetentionInfo(self.max_count)
        recurrence_info = Schedules.RecurrenceInfo(
                                    days=self.days,
                                    hour=self.hour,
                                    minute=self.minute)
        create_spec = Schedules.CreateSpec(
                                    location=self.location,
                                    location_user=self.location_user,
                                    location_password=self.location_password,
                                    recurrence_info=recurrence_info,
                                    retention_info=retention_info)

        self.schedule_client.create(self._schedule_id, create_spec)

    def update_schedule(self):
        retention_info = Schedules.RetentionInfo(self.max_count)
        recurrence_info = Schedules.RecurrenceInfo(
                                    days=self.days,
                                    hour=self.hour,
                                    minute=self.minute)
        update_spec = Schedules.UpdateSpec(
                                    location=self.location,
                                    location_user=self.location_user,
                                    location_password=self.location_password,
                                    recurrence_info=recurrence_info,
                                    retention_info=retention_info)

        self.schedule_client.update(self._schedule_id, update_spec)

    def get_schedule(self):
        self.schedule_client = Schedules(self.stub_config)
        schedule_spec = self.schedule_client.get(self._schedule_id)

        recurrence_info = schedule_spec.recurrence_info
        retention_info = schedule_spec.retention_info

        table = []
        data = [self._schedule_id,
                "{}:{}".format(recurrence_info.hour, recurrence_info.minute),
                " ".join(recurrence_info.days),
                retention_info.max_count]
        table.append(data)
        headers = ["Schedule ID", "Time", "Days", "Retention"]
        print(tabulate(table, headers))

    def run_backup(self):
        schedule_spec = self.schedule_client.run(self._schedule_id)

    def delete_schedule(self):
        self.schedule_client.delete(self._schedule_id)


def main():
    schedule = BackupSchedule()
    schedule.setup()
    schedule.run()

if __name__ == '__main__':
    main()
