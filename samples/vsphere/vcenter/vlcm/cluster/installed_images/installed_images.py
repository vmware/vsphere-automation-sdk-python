#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) 2024 Broadcom. All Rights Reserved.
* Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
* and/or its subsidiaries.
* SPDX-License-Identifier: MIT
* *******************************************************
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0.3+'

import time

from com.vmware.esx.settings.clusters_client import InstalledImages
from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.vcenter.hcl.utils import get_configuration

SUCCEEDED_KEY = "SUCCEEDED"
FAILED_KEY = "FAILED"

# With a 1 second sleep this is equal to roughly 5 minutes
TIME_OUT_ITERATIONS = 300


class InstalledImagesSvc:
    """
    Demonstrates triggering the "extract" workflow for the cluster Installed Images
    feature, waiting for the task to complete, and getting the result.

    Prerequisites:
        - A datacenter
        - A vSAN cluster with at least one host
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument("--cluster",
                            required=True,
                            help="MoID of the target cluster")
        args = sample_util.process_cli_args(parser.parse_args())

        self.cluster = args.cluster

        config = get_configuration(args.server, args.username,
                                   args.password,
                                   args.skipverification)

        self.apiClient = InstalledImages(config)

    def run(self):
        task = self.apiClient.extract_task(self.cluster)

        if self.waitForTask(task):
            print("Successfully got installed images report:")
            print(self.apiClient.get(self.cluster))

    def waitForTask(self, task):
        i = 0
        try:
            while True:
                i += 1
                status = task.get_info().status
                if status == SUCCEEDED_KEY or status == FAILED_KEY:
                    return True
                if i > TIME_OUT_ITERATIONS:
                    print("Timeout reached waiting for task--cancelling operation")
                    return False

                time.sleep(1)
        except Exception as e:
            print(f"Error occurred waiting for task: {e}")
            return False


def main():
    installedImagesSvc = InstalledImagesSvc()
    installedImagesSvc.run()


if __name__ == "__main__":
    main()
