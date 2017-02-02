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

from samples.vsphere.common import vapiconnect
from samples.vsphere.common.sample_util import parse_cli_args
from samples.vsphere.common.sample_util import pp
from com.vmware.vcenter_client import VM

"""
Demonstrates getting list of VMs present in vCenter
Sample Prerequisites:
vCenter/ESX
"""

stub_config = None
cleardata = False

def setup(context=None):
	global stub_config, cleardata
	server, username, password, cleardata, skip_verification = \
		parse_cli_args()
	stub_config = vapiconnect.connect(server,
									  username,
									  password,
									  skip_verification)
	#atexit.register(vapiconnect.logout, stub_config)


def run():
    list_vms(stub_config)


def list_vms(stub_config):
    """
    List VMs present in server
    """
    vm_svc = VM(stub_config)
    list_of_vms = vm_svc.list()
    for vm in list_of_vms:
        print ('{}'.format(vm))


def cleanup():
    pass


def main():
    try:
        setup()
        cleanup()
        run()
        if cleardata:
            cleanup()
    finally:
        if stub_config:
            vapiconnect.logout(stub_config)


if __name__ == '__main__':
    main()