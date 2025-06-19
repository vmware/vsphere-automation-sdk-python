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
__vcenter_version__ = '7.0+'

from os.path import dirname
from os.path import join as pjoin
from com.vmware.vcenter.vm_client import Power
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vapi.std.errors_client import NotFound
from samples.vsphere.common.sample_cli import build_arg_parser
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from pyVim.connect import (SmartConnect, Disconnect)
from pyVmomi import vim
import atexit
import configparser
import time
import ssl

# import CustomizationSpecManager from existing test case
custSpecMgrPath = pjoin(dirname(dirname(dirname(__file__))), "guest")
import sys
sys.path.append(custSpecMgrPath)
from customizationSpecs import CustomizationSpecManager

# inherit existing CustomizationSpecMananger to create a default linux
# customizationSpec for the following test


class NewCustomizationSpecManager(CustomizationSpecManager):
    def __init__(self, client):
        global custSpecMgrPath
        self.client = client
        self.specs_svc = client.vcenter.guest.CustomizationSpecs
        # get customization config
        self.config = configparser.ConfigParser()
        self.linCfgPath = pjoin(custSpecMgrPath, 'linSpec.cfg')
        self.specsAdded = []


class CustomizeVM(object):
    """
    Demo how to customize a virtual machine
    Sample Prerequisites:
    The sample needs an existing Linux VM with vmtools/open-vm-tools installed.
    """

    def __init__(self):
        parser = build_arg_parser()
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            help='Name of the testing vm')
        args = parser.parse_args()
        if args.vm_name:
            self.vm_name = args.vm_name
        else:
            raise Exception('Must specifiy an existing Linux VM for test' +
                            ' with "-n VM_NAME"')
        self.cleardata = args.cleardata
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)
        # get si
        sslContext = ssl._create_unverified_context()
        self.si = SmartConnect(host=args.server,
                               user=args.username,
                               pwd=args.password,
                               sslContext=sslContext)
        atexit.register(Disconnect, self.si)
        # init specs_svc and vmcust_svc
        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs
        self.vmcust_svc = self.client.vcenter.vm.guest.Customization
        self.custSpecMgr = NewCustomizationSpecManager(self.client)
        self.vm = get_vm(self.client, self.vm_name)
        if not self.vm:
            raise Exception('Need an existing Linux vm with name ({}).'
                            'Please create the vm first.'.format(self.vm_name))
        self.vmRef = self._getVmRef(vmName=self.vm_name)

    def _getVmRef(self, vmName=None):
        content = self.si.RetrieveContent()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
                for vm in vmList:
                    if vm.name == vmName:
                        return vm
        raise Exception("Cannot find the vm with name: {0}".format(vmName))

    def _findCustEvent(self, expectedEvent, tsBeforeQuery):
        vm = self.vmRef
        eventMgr = self.si.content.eventManager
        recOpt = vim.event.EventFilterSpec.RecursionOption()
        evtFilterEnt = \
            vim.event.EventFilterSpec.ByEntity(entity=vm,
                                               recursion=recOpt.self)
        evtFilterTime = \
            vim.event.EventFilterSpec.ByTime(beginTime=tsBeforeQuery)
        eventFilterSpec = vim.event.EventFilterSpec(entity=evtFilterEnt,
                                                    disableFullMessage=False,
                                                    time=evtFilterTime)
        eventList = eventMgr.QueryEvents(eventFilterSpec)
        for event in eventList:
            if isinstance(event, expectedEvent):
                print('Find expected customization Event %s' % expectedEvent)
                return True
        print('Did not find expected customization event, waiting...')

    def waitForCustEvent(self, expectedEvent, timeout):
        print('Waiting for customization event %s in %d seconds' %
              (expectedEvent, timeout))
        tsBeforeQuery = self.si.CurrentTime()
        timeout = time.time() + timeout
        while time.time() < timeout:
            if self._findCustEvent(expectedEvent, tsBeforeQuery):
                return True
            time.sleep(10)
        raise Exception('Timeout to find expected customization event')

    def setVM(self):
        print("Test Step: Using VM '{}' ({}) for Customize test".
              format(self.vm_name, self.vm))
        # create a linux customizationSpec
        self.custSpecMgr.parseLinuxCfg()
        self.specName = self.custSpecMgr.specName
        print("Test Step: Create a default Linux customizationSpec '{}'".
              format(self.specName))
        try:
            self.specs_svc.get(self.specName)
            print("Default customizationSpec '{}' exists. Skip creating".
                  format(self.specName))
        except NotFound:
            self.custSpecMgr.createLinuxSpec()
        self.setSpec = self.vmcust_svc.SetSpec(name=self.specName, spec=None)
        print('Test Step: Do VM customization by vAPI set method')
        # customize VM
        self.vmcust_svc.set(vm=self.vm, spec=self.setSpec)

    def powerOnVerify(self):
        print("Test Step: Power on VM '{}' and verify".format(self.vm_name))
        self.client.vcenter.vm.Power.start(self.vm)
        status = self.client.vcenter.vm.Power.get(self.vm)
        if status == Power.Info(state=Power.State.POWERED_ON):
            print('\nVM is powered on...')
        if self.waitForCustEvent(vim.event.CustomizationSucceeded, 900):
            print("Test PASS!")

    def cleanUp(self):
        vm = self.vm
        # clear customizationSpec
        self.custSpecMgr.deleteSpec()
        # Power off the vm if it is on
        status = self.client.vcenter.vm.Power.get(vm)
        if status == Power.Info(state=Power.State.POWERED_ON):
            print('\n#VM is powered on, power it off')
            self.client.vcenter.vm.Power.stop(vm)
            print('vm.Power.stop({})'.format(vm))
        status = self.client.vcenter.vm.Power.get(vm)
        if status == Power.Info(state=Power.State.POWERED_OFF):
            self.client.vcenter.VM.delete(vm)
            print("Deleted VM -- '{}-({})".format(self.vm_name, vm))


def main():
    myCustomizeVM = CustomizeVM()
    myCustomizeVM.setVM()
    myCustomizeVM.powerOnVerify()
    if myCustomizeVM.cleardata:
        print("Clean up in progress...")
        myCustomizeVM.cleanUp()


if __name__ == '__main__':
    main()
