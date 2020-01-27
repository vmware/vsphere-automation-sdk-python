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
__vcenter_version__ = '6.7+'

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import (sample_cli, sample_util)
from samples.vsphere.common.ssl_helper import get_unverified_session


"""
Demonstrates setting and getting TimeZone.Accepted values are

valid Timezone values for appliance

"""

parser = sample_cli.build_arg_parser()

parser.add_argument(
    '--time_sync',
    required=True,
    action='store',
    choices=['DISABLED', 'HOST'],
    help='DISABLED,time synchronization is disabled and HOST,Host time synchronization ')

args = sample_util.process_cli_args(parser.parse_args())
time_sync = args.time_sync

# Connect to vAPI services
session = get_unverified_session() if args.skipverification else None
client = create_vsphere_client(server=args.server,
                               username=args.username,
                               password=args.password,
                               session=session)
timesync_mode = client.appliance.Timesync.TimeSyncMode(time_sync)
print("Setting the appliance time syncronization as : " + time_sync)
client.appliance.Timesync.set(timesync_mode)
print("Timesync  as : " + client.appliance.Timesync.get())
