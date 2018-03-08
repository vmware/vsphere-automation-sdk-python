#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""
from vmware.vapi.vsphere.client import create_vsphere_client

__author__ = 'VMware, Inc.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm.hardware_client import Parallel
from pyVim.connect import SmartConnect, Disconnect

from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.common.ssl_helper import get_unverified_context, \
    get_unverified_session
from samples.vsphere.common.vim.file import delete_file
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.vcenter.setup import testbed

"""
Demonstrates how to configure Parallel ports for a VM.

Sample Prerequisites:
The sample needs an existing VM.
"""

vm = None
vm_name = None
client = None
service_instance = None
cleardata = False
parallels_to_delete = []
orig_parallel_summaries = None


def setup(context=None):
    global vm_name, client, service_instance, cleardata
    if context:
        # Run sample suite via setup script
        client = context.client
        vm_name = testbed.config['VM_NAME_DEFAULT']
        service_instance = context.service_instance
    else:
        # Run sample in standalone mode
        server, username, password, cleardata, skip_verification, vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])
        session = get_unverified_session() if skip_verification else None
        client = create_vsphere_client(server=server,
                                       username=username,
                                       password=password,
                                       session=session)

        context = None
        if skip_verification:
            context = get_unverified_context()
        service_instance = SmartConnect(host=server,
                                        user=username,
                                        pwd=password,
                                        sslContext=context)
        atexit.register(Disconnect, service_instance)


def run():
    global vm, client
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Parallel Sample".format(vm_name, vm))

    print('\n# Example: List all Parallel ports for a VM')
    parallel_summaries = client.vcenter.vm.hardware.Parallel.list(vm=vm)
    print('vm.hardware.Parallel.list({}) -> {}'.format(vm, parallel_summaries))

    # Save current list of Parallel ports to verify that we have cleaned up
    # properly
    global orig_parallel_summaries
    orig_parallel_summaries = parallel_summaries

    # Get information for each Parallel port on the VM
    for parallel_summary in parallel_summaries:
        parallel = parallel_summary.port
        parallel_info = client.vcenter.vm.hardware.Parallel.get(vm=vm,
                                                                port=parallel)
        print('vm.hardware.Parallel.get({}, {}) -> {}'.format(vm, parallel, pp(
            parallel_info)))

    # Make sure output file doesn't exist already
    cleanup_backends()

    print('\n# Example: Create Parallel port with defaults')
    parallel_create_spec = Parallel.CreateSpec()
    parallel = client.vcenter.vm.hardware.Parallel.create(vm, parallel_create_spec)
    print('vm.hardware.Parallel.create({}, {}) -> {}'.
          format(vm, parallel_create_spec, parallel))
    global parallels_to_delete
    parallels_to_delete.append(parallel)
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.format(vm, parallel,
                                                          pp(parallel_info)))

    print('\n# Example: Create Parallel port with FILE backing')
    parallel_port_datastore_path = testbed.config[
        'PARALLEL_PORT_DATASTORE_PATH']
    parallel_create_spec = Parallel.CreateSpec(
        start_connected=True,
        allow_guest_control=True,
        backing=Parallel.BackingSpec(type=Parallel.BackingType.FILE,
                                     file=parallel_port_datastore_path))
    parallel = client.vcenter.vm.hardware.Parallel.create(vm, parallel_create_spec)
    print('vm.hardware.Parallel.create({}, {}) -> {}'.
          format(vm, parallel_create_spec, parallel))
    parallels_to_delete.append(parallel)
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Example: Update Parallel port with same file but '
          'start_connected=False')
    print('#          and allow_guest_control=False')
    parallel_port_datastore_path = testbed.config[
        'PARALLEL_PORT_DATASTORE_PATH']
    parallel_update_spec = Parallel.UpdateSpec(
        start_connected=False,
        allow_guest_control=False,
        backing=Parallel.BackingSpec(type=Parallel.BackingType.FILE,
                                     file=parallel_port_datastore_path))
    client.vcenter.vm.hardware.Parallel.update(vm, parallel, parallel_update_spec)
    print('vm.hardware.Parallel.update({}, {}) -> {}'.
          format(vm, parallel_update_spec, parallel))
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.start(vm)
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Example: Connect Parallel port after powering on VM')
    client.vcenter.vm.hardware.Parallel.connect(vm, parallel)
    print('vm.hardware.Parallel.connect({}, {})'.format(vm, parallel))
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Example: Disconnect Parallel port while VM is powered on')
    client.vcenter.vm.hardware.Parallel.disconnect(vm, parallel)
    print('vm.hardware.Parallel.disconnect({}, {})'.format(vm, parallel))
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.stop(vm)
    parallel_info = client.vcenter.vm.hardware.Parallel.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    # List all Parallel ports for a VM
    parallel_summaries = client.vcenter.vm.hardware.Parallel.list(vm=vm)
    print('vm.hardware.Parallel.list({}) -> {}'.
          format(vm, parallel_summaries))

    # Always cleanup output file so the VM can be powered on next time
    cleanup_backends()


def cleanup():
    print('\n# Cleanup: Delete VM Parallel ports that were added')
    for parallel in parallels_to_delete:
        client.vcenter.vm.hardware.Parallel.delete(vm, parallel)
        print('vm.hardware.Parallel.delete({}, {})'.format(vm, parallel))

    parallel_summaries = client.vcenter.vm.hardware.Parallel.list(vm)
    print('vm.hardware.Parallel.list({}) -> {}'.format(vm, parallel_summaries))
    if set(orig_parallel_summaries) != set(parallel_summaries):
        print('vm.hardware.Parallel WARNING: '
              'Final Parallel ports info does not match original')


def cleanup_backends():
    """
    Cleanup after the parallel port samples.

    The files backing the serial port file backing needs to be removed or else
    the next time the VM is powered on and connected to the parallel port, the
    VM will post a question asking if the file should be Replaced or Appended.

    This is only an issue for backings that are write-only.
    """
    datacenter_name = testbed.config['PARALLEL_PORT_DATACENTER_NAME']
    datastore_path = testbed.config['PARALLEL_PORT_DATASTORE_PATH']
    delete_file(client,
                service_instance,
                'Parallel Port',
                datacenter_name,
                datastore_path)


def main():
    setup()
    cleanup_backends()
    run()
    if cleardata:
        cleanup()


if __name__ == '__main__':
    main()
