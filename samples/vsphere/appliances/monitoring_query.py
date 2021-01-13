#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2021. All Rights Reserved.
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
from datetime import datetime, timedelta

from samples.vsphere.common import (sample_cli, sample_util)
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Description: Demonstrates monitoring api workflow
1. List all memory and cpu counters
2. Query and print daily averages
"""

MEMORY_CATEGORY = "com.vmware.applmgmt.mon.cat.memory"
CPU_CATEGORY = "com.vmware.applmgmt.mon.cat.cpu"
CATEGORIES = (MEMORY_CATEGORY, CPU_CATEGORY)
METRIC_TITLE = "Metric"
DAY = timedelta(days=1)
DATE_FORMAT = "%Y-%m-%d"

parser = sample_cli.build_arg_parser()
args = sample_util.process_cli_args(parser.parse_args())
session = get_unverified_session() if args.skipverification else None
client = create_vsphere_client(server=args.server,
                               username=args.username,
                               password=args.password,
                               session=session)

# Get the Monitoring interface
monitoring = client.appliance.Monitoring

# List the available counters
counters = monitoring.list()

# Get the names of counters that relate to CPU and Memory categories
conterIds = []
for counter in counters:
    if counter.category in CATEGORIES:
        conterIds.append(counter.id)

# Compute interval for last few days
end = datetime.now()
start = end - timedelta(days=2)

# Query timeseries data
query = monitoring.MonitoredItemDataRequest(names=conterIds,
                            interval="DAY1",
                            function="AVG",
                            start_time=start,
                            end_time=end)
data = monitoring.query(query)


print("Example: Query Monitoring for Timeseries Data:")
print("-------------------\n")

# Create title and row format strings
# We need one labeled column for every day between start and end

# Reserve 25 characters for the first column with metric name
title = METRIC_TITLE + (" " * (25 - len(METRIC_TITLE)))
columnFormat = "{0:25}"

idx = 0
timestamp = start
# Create columns for each day
while timestamp <= end:
    # 24 characters per column. In the title use 10 for date and 14 padding.
    title += timestamp.strftime(DATE_FORMAT) + " " * 14
    columnFormat += "{{1[{}]:24}}".format(idx)
    # increment
    idx = idx + 1
    timestamp = timestamp + DAY

print(title)
for item in data:
    print(columnFormat.format(item.name, item.data))
