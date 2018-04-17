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

from tabulate import tabulate
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import vapiconnect
from com.vmware.appliance.recovery.backup.job_client import Details


class BackupJobList(object):
    """
    Demonstrates backup job list operation

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
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Connect to vAPI services
        self.stub_config = vapiconnect.connect(
                                    host=args.server,
                                    user=args.username,
                                    pwd=args.password,
                                    skip_verification=args.skipverification)

    def run(self):
        details_client = Details(self.stub_config)
        job_list = details_client.list()

        table = []
        for info in job_list.itervalues():
            row = [info.start_time.strftime("%b %d %Y %H:%M"),
                   info.duration,
                   info.type,
                   info.status,
                   info.location]
            table.append(row)
        headers = ["Start time", "Duration", "Type", "Status", "Location"]
        print(tabulate(table, headers))


def main():
    backup_job_list = BackupJobList()
    backup_job_list.setup()
    backup_job_list.run()


if __name__ == '__main__':
    main()
