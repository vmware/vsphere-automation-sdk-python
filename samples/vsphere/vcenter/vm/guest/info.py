#!/usr/bin/env python

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

import logging

from com.vmware.vcenter.vm_client import Power as HardPower
from com.vmware.vapi.std.errors_client import (NotFound, ServiceUnavailable)
from com.vmware.vcenter.vm.guest_client import Power
from com.vmware.vcenter.vm.guest_client import Identity
from com.vmware.vcenter.vm.guest_client import LocalFilesystem
from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.helper.guest_helper import \
    (wait_for_guest_info_ready, wait_for_guest_power_state)

"""
Demonstrates the virtual machine guest information.

Sample Prerequisites:
The sample needs an existing VM with VMware Tools.
"""


class GuestInfo(object):
    """
    Demonstrates guest information APIs
    Sample Prerequisites:
    vCenter/ESX
    """
    def __init__(self):
        server, username, password, self.cleardata, \
                   skip_verification, self.vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])

        session = get_unverified_session() if skip_verification else None
        self.vsphere_client = create_vsphere_client(server=server,
                                                    username=username,
                                                    password=password,
                                                    session=session)

        # Increase the logging level for more detailed output.
        # logging.basicConfig(level=logging.DEBUG)

    def run(self):
        # find the given VM
        self.vm = get_vm(self.vsphere_client, self.vm_name)
        if not self.vm:
            raise Exception('Sample requires an existing vm with name ({}).'
                            'Please create the vm first.'.format(self.vm_name))
        print("Using VM '{}' ({}) for Guest Info Sample"
              .format(self.vm_name, self.vm))

        # power on the VM if necessary
        status = self.vsphere_client.vcenter.vm.Power.get(self.vm)
        if status != HardPower.Info(state=HardPower.State.POWERED_ON):
            print('Powering on VM.')
            self.vsphere_client.vcenter.vm.Power.start(self.vm)

        # wait for guest info to be ready
        wait_for_guest_info_ready(self.vsphere_client, self.vm, 600)

        # get the Identity
        identity = self.vsphere_client.vcenter.vm.guest.Identity.get(self.vm)
        print('vm.guest.Identity.get({})'.format(self.vm))
        print('Identity: {}'.format(pp(identity)))

        # get the local filesystem info
        local_filesysteem = \
             self.vsphere_client.vcenter.vm.guest.LocalFilesystem.get(self.vm)
        print('vm.guest.LocalFilesystem.get({})'.format(self.vm))
        print('LocalFilesystem: {}'.format(pp(local_filesysteem)))

    def cleanup(self):
        # shut down the vm if requested
        if self.cleardata:
            print('\n# Cleanup: Shutdown the vm')
            self.vsphere_client.vcenter.vm.guest.Power.shutdown(self.vm)
            print('vm.guest.Power.shutdown({})'.format(self.vm))
            wait_for_guest_power_state(self.vsphere_client, self.vm,
                                       Power.State.NOT_RUNNING, 300)


def main():
    info = GuestInfo()
    info.run()
    info.cleanup()


if __name__ == '__main__':
    main()
