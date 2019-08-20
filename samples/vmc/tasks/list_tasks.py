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

import argparse
from com.vmware.vmc.model_client import Task
from vmware.vapi.vmc.client import create_vmc_client

"""
Demonstrates how to list tasks with given status

Sample Prerequisites:
    - VMware Cloud on AWS console API access
"""

accepted = [Task.STATUS_STARTED, Task.STATUS_CANCELING, Task.STATUS_FINISHED,
            Task.STATUS_FAILED, Task.STATUS_CANCELED]

parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

required_args = parser.add_argument_group(
        'required arguments')

required_args.add_argument(
        '--refresh_token',
        required=True,
        help='Refresh token obtained from CSP')
required_args.add_argument(
        '--org-id',
        required=True,
        help='Organization identifier.')

required_args.add_argument(
        '--task-status',
        help='Task status to filter. Possible values are: {} \
        Show all tasks if no value is passed'.format(accepted))

args = parser.parse_args()

vmc_client = create_vmc_client(args.refresh_token)

tasks = []

if args.task_status:
    status = args.task_status.upper()

    if status not in accepted:
        raise ValueError('Status "{}" is invalid, accept values are {}'.
                        format(args.task_status, accepted))

    tasks = vmc_client.orgs.Tasks.list(
        org=args.org_id, filter="(status eq '{}')".format(status))

    print('# List all "{}" tasks:\n'.format(status))
else:
    tasks = vmc_client.orgs.Tasks.list(org=args.org_id)
    print('# List all tasks:\n')

for task in tasks:
    print('{}\n'.format(task))
