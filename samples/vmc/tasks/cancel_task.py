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
Demonstrates how to cancel a running task

Sample Prerequisites:
    - VMware Cloud on AWS console API access
    - A running task
"""

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
        '--task-id',
        required=True,
        help='Task ID to be cancelled')

args = parser.parse_args()

vmc_client = create_vmc_client(args.refresh_token)

vmc_client.orgs.Tasks.update(org=args.org_id, task=args.task_id, action='cancel')

print('Task "{}" is cancelled'.format(args.task_id))
