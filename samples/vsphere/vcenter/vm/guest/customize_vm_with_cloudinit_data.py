#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2021. All Rights Reserved.
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
__copyright__ = 'Copyright 2021 VMware, Inc. All rights reserved.'
__vcenter_version__ = 'VCenter 7.0 U3'


import atexit
import os
import time
import ssl
from com.vmware.vcenter.guest_client import CustomizationSpec, \
    CloudConfiguration, CloudinitConfiguration, ConfigurationSpec, \
    GlobalDNSSettings
from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common.vim.helpers.vim_utils import get_obj
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from pyVim.connect import (SmartConnect, Disconnect)
from pyVmomi import vim
from vmware.vapi.vsphere.client import create_vsphere_client


class CustomizeVMWithCloudinitData(object):
    """
    Demo how to customize a virtual machine with cloud-init data
    Sample Prerequisites:
    This sample needs an existing Linux VM with both open-vm-tools
    version 11.3.0+ and cloud-init version 21.1+ installed
    """
    def __init__(self):
        self.metadata = None
        self.userdata = None
        self.specName = 'cloudinitDataSpec'
        self.specDesc =\
            'cloud-init data customization spec with metadata and userdata'
        self.parser = sample_cli.build_arg_parser()
        self.parser.add_argument('-n', '--vm_name', action='store',
                                 help='Name of the Linux vm')
        self.args = sample_util.process_cli_args(self.parser.parse_args())
        if self.args.vm_name is None:
            raise Exception('Must specify an existing Linux VM for test with '
                            '"-n VM_NAME"')
        self.session =\
            get_unverified_session() if self.args.skipverification else None
        self.client = create_vsphere_client(server=self.args.server,
                                            username=self.args.username,
                                            password=self.args.password,
                                            session=self.session)
        # get si
        self.sslContext = ssl._create_unverified_context()
        self.si = SmartConnect(host=self.args.server,
                               user=self.args.username,
                               pwd=self.args.password,
                               sslContext=self.sslContext)
        atexit.register(Disconnect, self.si)
        # init specs_svc and vmcust_svc
        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs
        self.vmcust_svc = self.client.vcenter.vm.guest.Customization
        self.vm = get_vm(self.client, self.args.vm_name)
        if self.vm is None:
            raise Exception('Need an existing Linux vm with name ({}). Please '
                            'create the vm first.'.format(self.args.vm_name))
        self.vmRef = self._getVmRef(vmName=self.args.vm_name)

    def _getVmRef(self, vmName=None):
        content = self.si.RetrieveContent()
        return get_obj(content, [vim.VirtualMachine], vmName)

    def _findCustEvent(self, expectedEvent, tsBeforeQuery):
        eventMgr = self.si.content.eventManager
        recOpt = vim.event.EventFilterSpec.RecursionOption()
        evtFilterEnt = \
            vim.event.EventFilterSpec.ByEntity(entity=self.vmRef,
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

    def createCloudinitDataSpec(self):
        """
        create a cloud-init data customizationSpec
        """
        print('------create 1 linux cloud-init data CustomizationSpec-------')
        metadataYamlFilePath = os.path.join(os.path.dirname(
                                            os.path.realpath(__file__)),
                                            '../../guest/sample_metadata.json')
        userdataFilePath = os.path.join(os.path.dirname(
                                        os.path.realpath(__file__)),
                                        '../../guest/sample_userdata')
        with open(metadataYamlFilePath, "r") as fp:
            self.metadata = fp.read().rstrip('\n')
        with open(userdataFilePath, "r") as fp:
            self.userdata = fp.read().rstrip('\n')
        cloudinitConfig = CloudinitConfiguration(metadata=self.metadata,
                                                 userdata=self.userdata)
        cloudConfig =\
            CloudConfiguration(cloudinit=cloudinitConfig,
                               type=CloudConfiguration.Type('CLOUDINIT'))
        configSpec = ConfigurationSpec(cloud_config=cloudConfig)
        globalDnsSettings = GlobalDNSSettings()
        adapterMappingList = []
        customizationSpec =\
            CustomizationSpec(configuration_spec=configSpec,
                              global_dns_settings=globalDnsSettings,
                              interfaces=adapterMappingList)
        createSpec = self.specs_svc.CreateSpec(name=self.specName,
                                               description=self.specDesc,
                                               spec=customizationSpec)
        self.specs_svc.create(spec=createSpec)
        print('Spec {} has been created'.format(self.specName))

    def setVM(self):
        print('---customize VM {} with cloud-init data CustomizationSpec---'.
              format(self.args.vm_name))
        # create a linux cloud-init data customizationSpec
        self.createCloudinitDataSpec()
        setSpec = self.vmcust_svc.SetSpec(name=self.specName, spec=None)
        # customize VM with the created cloud-init data customizationSpec
        self.vmcust_svc.set(vm=self.vm, spec=setSpec)

    def waitForCustEvent(self, expectedEvent, timeout):
        print('Waiting for customization event {} in {} seconds'.
              format(expectedEvent, timeout))
        currentTime = self.si.CurrentTime()
        timeout = time.time() + timeout
        while time.time() < timeout:
            if self._findCustEvent(expectedEvent, currentTime):
                return True
            time.sleep(10)
        raise Exception('Timeout to find expected customization event')

    def powerOnAndVerifyCustomizationResult(self):
        print('---power on VM {} and verify customization result---'.
              format(self.args.vm_name))
        self.client.vcenter.vm.Power.start(self.vm)
        if self.waitForCustEvent(vim.event.CustomizationSucceeded, 900):
            print("Test PASS!")


def main():
    customizeVMWithCloudinitData = CustomizeVMWithCloudinitData()
    customizeVMWithCloudinitData.setVM()
    customizeVMWithCloudinitData.powerOnAndVerifyCustomizationResult()


if __name__ == '__main__':
    main()
