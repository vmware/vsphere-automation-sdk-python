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

from com.vmware.vcenter.guest_client import CustomizationSpec, \
    CloudConfiguration, CloudinitConfiguration, ConfigurationSpec, \
    GlobalDNSSettings
from pprint import pprint
from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from vmware.vapi.vsphere.client import create_vsphere_client
import os


class CloudinitDataCustomizationSpecs(object):
    """
    Demonstrates create/list/get/set/delete cloud-init data customizationSpecs
    Sample Prerequisites: 1 vcenter, no ESXi nor VM needed
    """
    def __init__(self):
        self.metadata = None
        self.userdata = None
        self.parser = sample_cli.build_arg_parser()
        self.args = sample_util.process_cli_args(self.parser.parse_args())
        self.session =\
            get_unverified_session() if self.args.skipverification else None
        self.client = create_vsphere_client(server=self.args.server,
                                            username=self.args.username,
                                            password=self.args.password,
                                            session=self.session)
        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs

    def createCloudinitDataSpec(self, specName, specDesc):
        """
        create a cloud-init data customizationSpec
        """
        print('------create 1 linux cloud-init data CustomizationSpec-------')
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
        createSpec = self.specs_svc.CreateSpec(name=specName,
                                               description=specDesc,
                                               spec=customizationSpec)
        self.specs_svc.create(spec=createSpec)
        print('{} has been created'.format(specName))
        print('-------------------------------------------------------------')

    def createSpecWithMetadataInYamlAndUserdata(self):
        """
        create a linux cloud-init data customizationSpec with metadata in yaml
        format and userdata
        """
        metadataYamlFilePath = os.path.join(os.path.dirname(
                                            os.path.realpath(__file__)),
                                            'sample_metadata.yaml')
        userdataFilePath = os.path.join(os.path.dirname(
                                        os.path.realpath(__file__)),
                                        'sample_userdata')
        with open(metadataYamlFilePath, "r") as fp:
            self.metadata = fp.read().rstrip('\n')
        with open(userdataFilePath, "r") as fp:
            self.userdata = fp.read().rstrip('\n')
        self.createCloudinitDataSpec('specWithMetadataInYamlAndUserdata',
                                     'linux cloud-init data customization spec'
                                     'with metadata in yaml format and '
                                     'userdata')

    def createSpecWithMetadataInJsonAndUserdata(self):
        """
        create a linux cloud-init data customizationSpec with metadata in json
        format and userdata
        """
        metadataYamlFilePath = os.path.join(os.path.dirname(
                                            os.path.realpath(__file__)),
                                            'sample_metadata.json')
        userdataFilePath = os.path.join(os.path.dirname(
                                        os.path.realpath(__file__)),
                                        'sample_userdata')
        with open(metadataYamlFilePath, "r") as fp:
            self.metadata = fp.read().rstrip('\n')
        with open(userdataFilePath, "r") as fp:
            self.userdata = fp.read().rstrip('\n')
        self.createCloudinitDataSpec('specWithMetadataInJsonAndUserdata',
                                     'linux cloud-init data customization spec'
                                     'with metadata in json format and '
                                     'userdata')

    def createSpecWithMetadataOnly(self):
        """
        create a linux cloud-init data customizationSpec with metadata in yaml
        format and without userdata
        """
        metadataYamlFilePath = os.path.join(os.path.dirname(
                                            os.path.realpath(__file__)),
                                            'sample_metadata.yaml')
        with open(metadataYamlFilePath, "r") as fp:
            self.metadata = fp.read().rstrip('\n')
        self.createCloudinitDataSpec('specWithMetadataOnly',
                                     'linux cloud-init data customization spec'
                                     'with metadata only')

    def listCustomizationSpecs(self):
        print('------list all existing customization Spec------')
        existingSpecs = self.specs_svc.list()
        if (len(existingSpecs) > 0):
            pprint(existingSpecs)
        else:
            print('no specs found')
        print('------------------------------------------------')

    def getSetCloudinitDataCustomizationSpec(self):
        print('------get an existing cloud-init data customization Spec------')
        existingSpecs = self.specs_svc.list()
        if (len(existingSpecs) > 0):
            existingSpecName = existingSpecs[0].name
            existingSpec = self.specs_svc.get(existingSpecName)
            pprint(existingSpec)
            # Set a new spec description
            newSpecDesc =\
                '{} updated by vapi set() method'.format(existingSpecName)
            existingSpec.spec.description = newSpecDesc
            # Set a new metadata
            metadata =\
                """
                instance-id: test-vm-id-01-updated
                local-hostname: test-vm-01-updated
                network:
                    version: 2
                    ethernets:
                        ens160:
                            match:
                                name: ens*
                            dhcp4: yes
                """
            existingSpec.spec.spec.configuration_spec.cloud_config.cloudinit.\
                metadata = metadata
            print('------set existing cloud-init data customizationSpec------')
            self.specs_svc.set(name=existingSpecName, spec=existingSpec.spec)
            print('{} has been set'.format(existingSpecName))
            pprint(existingSpec)
        else:
            print('no specs found')
        print('-------------------------------------------------------------')

    def deleteCustomizationSpecs(self):
        print('-----delete existing customization Specs-----')
        existingSpecs = self.specs_svc.list()
        if (len(existingSpecs) > 0):
            for i in range(len(existingSpecs)):
                specName = existingSpecs[i].name
                self.specs_svc.delete(specName)
                print('{} has been deleted'.format(specName))
        else:
            print('no specs found')
        print('-------------------------------------------------------------')


def main():
    cloudinitDataCustomizationSpecs = CloudinitDataCustomizationSpecs()
    cloudinitDataCustomizationSpecs.createSpecWithMetadataInYamlAndUserdata()
    cloudinitDataCustomizationSpecs.createSpecWithMetadataInJsonAndUserdata()
    cloudinitDataCustomizationSpecs.createSpecWithMetadataOnly()
    cloudinitDataCustomizationSpecs.listCustomizationSpecs()
    cloudinitDataCustomizationSpecs.getSetCloudinitDataCustomizationSpec()
    cloudinitDataCustomizationSpecs.deleteCustomizationSpecs()


if __name__ == '__main__':
    main()
