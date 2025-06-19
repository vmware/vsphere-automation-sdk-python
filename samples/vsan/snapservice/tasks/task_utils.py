"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

import time

from com.vmware.snapservice.tasks_client import Status

from samples.vsan.snapservice.tasks.get_task import GetTask


def wait_for_snapservice_task(snapservice_client, ss_task_id):
    """
    Wait for the snapservice task to complete.
    """
    task = GetTask(snapservice_client, ss_task_id)
    while True:
        task_info = task.get_task()

        if task_info.status == Status.SUCCEEDED:
            print("# Task {} succeeds.".format(task_info.description.id))
            return
        elif task_info.status == Status.FAILED:
            print("# Task {} fails.\nError:\n".format(task_info.description.id))
            print(task_info.error)
            return
        else:
            print("# Task {} progress: {}".format(task_info.description.id,
                                                  task_info.progress.completed))
            time.sleep(5)
