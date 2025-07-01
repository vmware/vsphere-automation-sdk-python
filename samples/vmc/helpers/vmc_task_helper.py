"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017, 2018. All Rights Reserved.
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

from time import sleep

from com.vmware.vmc.model_client import Task


def wait_for_task(task_client, org_id, task_id, interval_sec=60):
    """
    Helper method to wait for a task to finish
    :param task_client: task client to query the task object
    :param org_id: organization id
    :param task_id: task id
    :param interval_sec: task pulling interval_sec in sec
    :return: True if task finished successfully, False otherwise.
    """
    print('Wait for task {} to finish'.format(task_id))
    print('Checking task status every {} seconds'.format(interval_sec))

    while True:
        task = task_client.get(org_id, task_id)

        if task.status == Task.STATUS_FINISHED:
            print('\nTask {} finished successfully'.format(task_id))
            return True
        elif task.status == Task.STATUS_FAILED:
            print('\nTask {} failed'.format(task_id))
            return False
        elif task.status == Task.STATUS_CANCELED:
            print('\nTask {} cancelled'.format(task_id))
            return False
        else:
            print("Estimated time remaining: {} minutes".format(
                task.estimated_remaining_minutes))
            sleep(interval_sec)


def list_all_tasks(task_client, org_id):
    """
    List all tasks in a given org
    :param task_client: task client to query the task object
    :param org_id: organization id
    """
    tasks = task_client.list(org_id)
    for task in tasks:
        print('ID: {}, Status: {}, Progress: {}, Started: {}, User: {}'.format(
            task.id, task.status, task.progress_percent, task.start_time,
            task.user_name))
