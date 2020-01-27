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

import time
import logging
from com.vmware.vcenter.vm.guest_client import Power
from com.vmware.vcenter.vm.guest_client import Identity
from com.vmware.vapi.std.errors_client import (NotFound, ServiceUnavailable)


def wait_for_guest_info_ready(vsphere_client, vmId, timeout):
    """
    Waits for the Tools info to be ready, or times out.
    """
    print('Waiting for guest info to be ready.')
    start = time.time()
    timeout = start + timeout
    while timeout > time.time():
        logging.info('Waiting for guest info to be ready')
        time.sleep(1)
        try:
            result = vsphere_client.vcenter.vm.guest.Identity.get(vmId)
            break
        except ServiceUnavailable as e:
            logging.debug('Got ServiceUnavailable waiting for guest info')
            pass
        except Exception as e:
            print('Unexpected exception %s waiting for guest info' % e)
            raise e
    if time.time() >= timeout:
        raise Exception('Timed out waiting for guest info to be available.\n'
                        'Be sure the VM has VMware Tools.')
    else:
        logging.info('Took %d seconds for guest info to be available'
                     % (time.time() - start))


def wait_for_guest_power_state(vsphere_client, vmId, desiredState, timeout):
    """
    Waits for the guest to reach the desired power state, or times out.
    """
    print("Waiting for guest power state {}".format(desiredState))
    start = time.time()
    timeout = start + timeout
    while timeout > time.time():
        time.sleep(1)
        curState = vsphere_client.vcenter.vm.guest.Power.get(vmId).state
        logging.debug('Current guest power state is %s, looking for %s'
                      % (curState, desiredState))
        if desiredState == curState:
            break
    if desiredState != curState:
        raise Exception('Timed out waiting for guest to reach desired power state')
    else:
        logging.info('Took %s seconds for guest power state to change to %s'
                     % (time.time() - start, desiredState))


def wait_for_power_operations_state(vsphere_client, vmId, desiredState, timeout):
    """
    Waits for the desired soft power operations state, or times out.
    """
    print('Waiting for guest power operations to be {}'.format(desiredState))
    start = time.time()
    timeout = start + timeout
    while timeout > time.time():
        time.sleep(1)
        curState = vsphere_client.vcenter.vm.guest.Power.get(vmId).operations_ready
        logging.debug('Current guest operations ready state is %s,'
                      ' looking for %s' % (curState, desiredState))
        if desiredState == curState:
            break
    if desiredState != curState:
        raise Exception('Timed out waiting for guest to reach desired '
                        ' operations ready state')
    else:
        logging.info('Took %s seconds for guest operations ready state\
                     to change to %s' % (time.time() - start, desiredState))
