#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '9.0+'

import pyVim.connect  # noqa: E402
import pyVim.task  # noqa: E402
from pyVmomi import vim  # noqa: E402

from samples.vsphere.common import sample_cli   # noqa: E402
from samples.vsphere.common import sample_util  # noqa: E402
from samples.vsphere.common.ssl_helper import get_unverified_context  # noqa: E402


class ReconfigureVM(object):
    """
    Demonstrates how to reconfigure a VM to connect it's vnic to a subnet

    Prerequisites:
        - Projects/VPCs/Subnets created
        - A VM with at least one network adapter
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            help='Name of the testing vm')
        parser.add_argument('-t', '--subnet_id',
                            action='store',
                            help='Id of the subnet')
        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vm_name
        self.subnet_id = args.subnet_id

        context = get_unverified_context() if args.skipverification else None
        self.service_instance = pyVim.connect.SmartConnect(host=args.server,
                                                           user=args.username,
                                                           pwd=args.password,
                                                           sslContext=context)

    def run(self):
        content = self.service_instance.RetrieveContent()
        container_VM = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True)

        found = False
        for vm in container_VM.view:
            if vm.name != self.vm_name:
                continue

            found = True
            nicSpec = vim.vm.device.VirtualDeviceSpec()
            nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nicSpec.device = vim.vm.device.VirtualVmxnet3()
            nicSpec.device.key = 4000
            nicSpec.device.subnetId = self.subnet_id

            spec = vim.vm.ConfigSpec()
            spec.deviceChange = [nicSpec]

            task = vm.Reconfigure(spec)
            pyVim.task.WaitForTask(task)
            print("VM reconfigure done.")

        if not found:
            print("VM not found.")


def main():
    reconfigureVM = ReconfigureVM()
    reconfigureVM.run()


if __name__ == '__main__':
    main()
