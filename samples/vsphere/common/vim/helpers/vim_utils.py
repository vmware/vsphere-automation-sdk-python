"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013. All Rights Reserved.
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
__copyright__ = 'Copyright 2013 VMware, Inc. All rights reserved.'

from pyVmomi import vim, vmodl

_views = []  # list of container views


def get_obj(content, vimtype, name):
    """
     Get the vsphere managed object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    _views.append(container)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def get_obj_by_moId(content, vimtype, moid):
    """
    Get the vsphere managed object by moid value
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    _views.append(container)
    for c in container.view:
        if c._GetMoId() == moid:
            obj = c
            break
    return obj


def delete_object(content, mo):
    """
    Deletes a vsphere managed object and waits for the deletion to complete
    """
    print('Deleting {0}'.format(mo._GetMoId()))
    try:
        wait_for_tasks(content, [mo.Destroy()])
        print('Deleted {0}'.format(mo._GetMoId()))
    except Exception:
        print('Unexpected error while deleting managed object {0}'.format(
            mo._GetMoId()))
        return False
    return True


def poweron_vm(content, mo):
    """
    Powers on a VM and wait for power on operation to complete
    """
    if not isinstance(mo, vim.VirtualMachine):
        return False

    print('Powering on vm {0}'.format(mo._GetMoId()))
    try:
        wait_for_tasks(content, [mo.PowerOn()])
        print('{0} powered on successfully'.format(mo._GetMoId()))
    except Exception:
        print('Unexpected error while powering on vm {0}'.format(mo._GetMoId()))
        return False
    return True


def poweroff_vm(content, mo):
    """
    Powers on a VM and wait for power on operation to complete
    """
    if not isinstance(mo, vim.VirtualMachine):
        return False

    print('Powering off vm {0}'.format(mo._GetMoId()))
    try:
        wait_for_tasks(content, [mo.PowerOff()])
        print('{0} powered off successfully'.format(mo._GetMoId()))
    except Exception:
        print(
            'Unexpected error while powering off vm {0}'.format(mo._GetMoId()))
        return False
    return True


def wait_for_tasks(content, tasks):
    """
    Given the tasks, it returns after all the tasks are complete
    """
    taskList = [str(task) for task in tasks]

    # Create filter
    objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task) for task in
                tasks]
    propSpec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                          pathSet=[], all=True)
    filterSpec = vmodl.query.PropertyCollector.FilterSpec()
    filterSpec.objectSet = objSpecs
    filterSpec.propSet = [propSpec]
    task_filter = content.propertyCollector.CreateFilter(filterSpec, True)

    try:
        version, state = None, None

        # Loop looking for updates till the state moves to a completed state.
        while len(taskList):
            update = content.propertyCollector.WaitForUpdates(version)
            for filterSet in update.filterSet:
                for objSet in filterSet.objectSet:
                    task = objSet.obj
                    for change in objSet.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in taskList:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            taskList.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if task_filter:
            task_filter.Destroy()


def __destroy_container_views():
    for view in _views:
        try:
            view.Destroy()
        except vmodl.fault.ManagedObjectNotFound:
            pass  # silently bypass the exception if the objects are already deleted/not found on the server


import atexit

atexit.register(__destroy_container_views)
