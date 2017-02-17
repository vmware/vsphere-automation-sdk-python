#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.5+'

import atexit

from com.vmware.vcenter.vm.hardware_client import Parallel
from com.vmware.vcenter.vm_client import Power
from pyVim.connect import SmartConnect, Disconnect

from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.common.ssl_helper import get_unverified_context
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
stub_config = None
service_instance = None
parallel_svc = None
cleardata = False
parallels_to_delete = []
orig_parallel_summaries = None


def setup(context=None):
    global vm_name, stub_config, service_instance, cleardata
    if context:
        # Run sample suite via setup script
        stub_config = context.stub_config
        vm_name = testbed.config['VM_NAME_DEFAULT']
        service_instance = context.service_instance
    else:
        # Run sample in standalone mode
        server, username, password, cleardata, skip_verification, vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])
        stub_config = vapiconnect.connect(server,
                                          username,
                                          password,
                                          skip_verification)
        atexit.register(vapiconnect.logout, stub_config)

        context = None
        if skip_verification:
            context = get_unverified_context()
        service_instance = SmartConnect(host=server,
                                        user=username,
                                        pwd=password,
                                        sslContext=context)
        atexit.register(Disconnect, service_instance)


def run():
    global vm, parallel_svc
    vm = get_vm(stub_config, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Parallel Sample".format(vm_name, vm))

    # Create Parallel port stub used for making requests
    parallel_svc = Parallel(stub_config)
    vm_power_svc = Power(stub_config)

    print('\n# Example: List all Parallel ports for a VM')
    parallel_summaries = parallel_svc.list(vm=vm)
    print('vm.hardware.Parallel.list({}) -> {}'.format(vm, parallel_summaries))

    # Save current list of Parallel ports to verify that we have cleaned up
    # properly
    global orig_parallel_summaries
    orig_parallel_summaries = parallel_summaries

    # Get information for each Parallel port on the VM
    for parallel_summary in parallel_summaries:
        parallel = parallel_summary.port
        parallel_info = parallel_svc.get(vm=vm, port=parallel)
        print('vm.hardware.Parallel.get({}, {}) -> {}'.format(vm, parallel, pp(
            parallel_info)))

    print('\n# Example: Create Parallel port with defaults')
    parallel_create_spec = Parallel.CreateSpec()
    parallel = parallel_svc.create(vm, parallel_create_spec)
    print('vm.hardware.Parallel.create({}, {}) -> {}'.
          format(vm, parallel_create_spec, parallel))
    global parallels_to_delete
    parallels_to_delete.append(parallel)
    parallel_info = parallel_svc.get(vm, parallel)
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
    parallel = parallel_svc.create(vm, parallel_create_spec)
    print('vm.hardware.Parallel.create({}, {}) -> {}'.
          format(vm, parallel_create_spec, parallel))
    parallels_to_delete.append(parallel)
    parallel_info = parallel_svc.get(vm, parallel)
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
    parallel_svc.update(vm, parallel, parallel_update_spec)
    print('vm.hardware.Parallel.update({}, {}) -> {}'.
          format(vm, parallel_update_spec, parallel))
    parallel_info = parallel_svc.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.start(vm)
    parallel_info = parallel_svc.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Example: Connect Parallel port after powering on VM')
    parallel_svc.connect(vm, parallel)
    print('vm.hardware.Parallel.connect({}, {})'.format(vm, parallel))
    parallel_info = parallel_svc.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Example: Disconnect Parallel port while VM is powered on')
    parallel_svc.disconnect(vm, parallel)
    print('vm.hardware.Parallel.disconnect({}, {})'.format(vm, parallel))
    parallel_info = parallel_svc.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    vm_power_svc.stop(vm)
    parallel_info = parallel_svc.get(vm, parallel)
    print('vm.hardware.Parallel.get({}, {}) -> {}'.
          format(vm, parallel, pp(parallel_info)))

    # List all Parallel ports for a VM
    parallel_summaries = parallel_svc.list(vm=vm)
    print('vm.hardware.Parallel.list({}) -> {}'.
          format(vm, parallel_summaries))


def cleanup():
    print('\n# Cleanup: Delete VM Parallel ports that were added')
    for parallel in parallels_to_delete:
        parallel_svc.delete(vm, parallel)
        print('vm.hardware.Parallel.delete({}, {})'.format(vm, parallel))

    parallel_summaries = parallel_svc.list(vm)
    print('vm.hardware.Parallel.list({}) -> {}'.format(vm, parallel_summaries))
    if set(orig_parallel_summaries) != set(parallel_summaries):
        print('vm.hardware.Parallel WARNING: '
              'Final Parallel ports info does not match original')

    cleanup_backends()


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
    delete_file(stub_config,
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
