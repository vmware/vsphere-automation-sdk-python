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

__author__ = 'VMware, Inc.'
__vcenter_version__ = '6.5+'

import atexit

from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.vcenter.vm.hardware_client import Serial
from pyVim.connect import SmartConnect, Disconnect

from samples.vsphere.common.sample_util import parse_cli_args_vm
from samples.vsphere.common.sample_util import pp
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vim.file import delete_file
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.common.ssl_helper import get_unverified_session

"""
Demonstrates how to configure Serial ports for a VM.

Sample Prerequisites:
The sample needs an existing VM.

Note:
The sample adds new serial ports to the existing VM. If you re-run the sample
without cleaning up the previous created serial ports, the VM may be stuck at
power on stage as there will be multiple serial ports using the same output
file. In such case, you will see a question in vCenter UI asking if the file
should be Replaced or Appended.
To avoid this, make sure to pass -c to clean up the serial ports or manually
delete them after running the sample.
"""

vm = None
vm_name = None
client = None
service_instance = None
cleardata = False
serials_to_delete = []
orig_serial_summaries = None


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

        # Connect to vSphere client
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
    # * Backings types are FILE, HOST_DEVICE, PIPE_SERVER, PIPE_CLIENT,
    # NETWORK_SERVER, NETWORK_CLIENT
    #   * NetworkLocation: See
    # https://kb.vmware.com/selfservice/microsites/search.do?language=en_US
    # &cmd=displayKC&externalId=2004954
    #   * Proxy: https://www.vmware.com/support/developer/vc-sdk/visdk41pubs
    # /vsp41_usingproxy_virtual_serial_ports.pdf

    global vm
    vm = get_vm(client, vm_name)
    if not vm:
        raise Exception('Sample requires an existing vm with name ({}). '
                        'Please create the vm first.'.format(vm_name))
    print("Using VM '{}' ({}) for Serial Sample".format(vm_name, vm))

    print('\n# Example: List all Serial ports for a VM')
    serial_summaries = client.vcenter.vm.hardware.Serial.list(vm=vm)
    print('vm.hardware.Serial.list({}) -> {}'.format(vm, serial_summaries))

    # Save current list of Serial ports to verify that we have cleaned up
    # properly
    global orig_serial_summaries
    orig_serial_summaries = serial_summaries

    # Get information for each Serial port on the VM
    for serial_summary in serial_summaries:
        serial = serial_summary.port
        serial_info = client.vcenter.vm.hardware.Serial.get(vm=vm, port=serial)
        print('vm.hardware.Serial.get({}, {}) -> {}'.format(vm, serial,
                                                            pp(serial_info)))

    global serials_to_delete

    print('\n# Example: Create Serial port with defaults')
    serial_create_spec = Serial.CreateSpec()
    serial = client.vcenter.vm.hardware.Serial.create(vm, serial_create_spec)
    print('vm.hardware.Serial.create({}, {}) -> {}'.
          format(vm, serial_create_spec, serial))
    serials_to_delete.append(serial)
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    # Make sure output file doesn't exist already
    cleanup_backends()

    print('\n# Example: Create Serial port with FILE backing')
    serial_port_datastore_path = testbed.config['SERIAL_PORT_DATASTORE_PATH']
    serial_create_spec = Serial.CreateSpec(
        start_connected=True,
        allow_guest_control=True,
        backing=Serial.BackingSpec(type=Serial.BackingType.FILE,
                                   file=serial_port_datastore_path))
    serial = client.vcenter.vm.hardware.Serial.create(vm, serial_create_spec)
    print('vm.hardware.Serial.create({}, {}) -> {}'.
          format(vm, serial_create_spec, serial))
    serials_to_delete.append(serial)
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Example: Create Serial port to use NETWORK_SERVER')
    serial_port_network_server_location = \
        testbed.config['SERIAL_PORT_NETWORK_SERVER_LOCATION']
    serial_create_spec = Serial.CreateSpec(
        start_connected=True,
        allow_guest_control=True,
        backing=Serial.BackingSpec(type=Serial.BackingType.NETWORK_SERVER,
                                   network_location=serial_port_network_server_location))
    serial = client.vcenter.vm.hardware.Serial.create(vm, serial_create_spec)
    print('vm.hardware.Serial.create({}, {}) -> {}'.
          format(vm, serial_create_spec, serial))
    serials_to_delete.append(serial)
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Example: Update Serial port to use NETWORK_CLIENT')
    serial_port_network_client_location = \
        testbed.config['SERIAL_PORT_NETWORK_CLIENT_LOCATION']
    serial_port_network_proxy = testbed.config['SERIAL_PORT_NETWORK_PROXY']
    serial_update_spec = Serial.UpdateSpec(
        start_connected=False,
        allow_guest_control=False,
        backing=Serial.BackingSpec(type=Serial.BackingType.NETWORK_CLIENT,
                                   network_location=serial_port_network_client_location,
                                   proxy=serial_port_network_proxy))
    client.vcenter.vm.hardware.Serial.update(vm, serial, serial_update_spec)
    print('vm.hardware.Serial.update({}, {}) -> {}'.
          format(vm, serial_update_spec, serial))
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Starting VM to run connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.start(vm)
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Example: Connect Serial port after powering on VM')
    client.vcenter.vm.hardware.Serial.connect(vm, serial)
    print('vm.hardware.Serial.connect({}, {})'.format(vm, serial))
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Example: Disconnect Serial port while VM is powered on')
    client.vcenter.vm.hardware.Serial.disconnect(vm, serial)
    print('vm.hardware.Serial.disconnect({}, {})'.format(vm, serial))
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    print('\n# Stopping VM after connect/disconnect sample')
    print('vm.Power.start({})'.format(vm))
    client.vcenter.vm.Power.stop(vm)
    serial_info = client.vcenter.vm.hardware.Serial.get(vm, serial)
    print('vm.hardware.Serial.get({}, {}) -> {}'.
          format(vm, serial, pp(serial_info)))

    # List all Serial ports for a VM
    serial_summaries = client.vcenter.vm.hardware.Serial.list(vm=vm)
    print('vm.hardware.Serial.list({}) -> {}'.format(vm, serial_summaries))

    # Always cleanup output file so the VM can be powered on next time
    cleanup_backends()


def cleanup():
    print('\n# Delete VM Serial ports that were added')
    for serial in serials_to_delete:
        client.vcenter.vm.hardware.Serial.delete(vm, serial)
        print('vm.hardware.Serial.delete({}, {})'.format(vm, serial))

    serial_summaries = client.vcenter.vm.hardware.Serial.list(vm)
    print('vm.hardware.Serial.list({}) -> {}'.format(vm, serial_summaries))
    if set(orig_serial_summaries) != set(serial_summaries):
        print('vm.hardware.Serial WARNING: '
              'Final Serial ports info does not match original')


def cleanup_backends():
    """
    Cleanup after the serial port samples.

    The files backing the serial port file backing needs to be removed or else
    the next time the VM is powered on and connected to the serial port, the VM
    will post a question asking if the file should be Replaced or Appended.

    This is only an issue for backings that are write-only.
    """
    datacenter_name = testbed.config['SERIAL_PORT_DATACENTER_NAME']
    datastore_path = testbed.config['SERIAL_PORT_DATASTORE_PATH']
    delete_file(client,
                service_instance,
                'Serial Port',
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
