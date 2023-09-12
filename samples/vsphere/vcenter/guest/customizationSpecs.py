#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2020. All Rights Reserved.
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
__copyright__ = 'Copyright 2020 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0+'

from pprint import pprint
import configparser
import os

from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session

from com.vmware.vcenter.guest_client import (CustomizationSpec,
                                             HostnameGenerator,
                                             LinuxConfiguration,
                                             ConfigurationSpec,
                                             GlobalDNSSettings,
                                             AdapterMapping,
                                             IPSettings,
                                             Ipv4,
                                             Ipv6,
                                             Ipv6Address)
from com.vmware.vcenter.guest_client import (WindowsConfiguration,
                                             WindowsSysprep,
                                             Domain,
                                             GuiUnattended,
                                             UserData,
                                             WindowsNetworkAdapterSettings)


class CustomizationSpecManager(object):
    """
    Demonstrates create/list/get/set/delete customizationSpecs in vCenter
    Sample Prerequisites: 1 vcenter, no ESXi nor VM needed
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-x', '--win_password',
                            action='store',
                            help='windows admin password to be customized')
        args = sample_util.process_cli_args(parser.parse_args())
        if args.win_password:
            self.win_password = args.win_password
        else:
            self.win_password = None
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)
        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs
        # get customization config
        self.config = configparser.ConfigParser()
        self.linCfgPath = os.path.join(os.path.dirname(
                                       os.path.realpath(__file__)),
                                       'linSpec.cfg')
        self.winCfgPath = os.path.join(os.path.dirname(
                                       os.path.realpath(__file__)),
                                       'winSpec.cfg')
        self.specsAdded = []

    # common method to parse specInfo for linux/windows spec
    def parseSpecInfo(self):
        self.specName = self.config['CREATESPEC']['specName']
        self.specDesc = self.config['CREATESPEC']['specDesc']

    # common method to parse network cfg for linux/windows spec
    def parseNetwork(self):
        # parse macAddress
        self.macAddress = self.config['NETWORK'].get('macAddress')
        # parse ipv4
        self.ipv4Type = self.config['NETWORK'].get('ipv4Type', 'DHCP')
        if self.ipv4Type == 'STATIC':
            self.ipv4_prefix = self.config['NETWORK'].getint('ipv4_prefix')
            self.ipv4_gateways = self.config['NETWORK'].get('ipv4_gateways')
            if self.ipv4_gateways is not None:
                self.ipv4_gateways = self.ipv4_gateways.split(',')
            self.ipv4_ip = self.config['NETWORK'].get('ipv4_ip')
        elif (self.ipv4Type == 'DHCP' or
              self.ipv4Type == 'USER_INPUT_REQUIRED'):
            self.ipv4_prefix = None
            self.ipv4_gateways = None
            self.ipv4_ip = None
        else:
            raise Exception('Wrong ipv4Type "{}"'.format(self.ipv4Type))
        # parse ipv6
        self.ipv6Type = self.config['NETWORK'].get('ipv6Type')
        if self.ipv6Type == 'STATIC':
            self.ipv6_prefix = self.config['NETWORK'].getint('ipv6_prefix')
            self.ipv6_gateways = self.config['NETWORK'].get('ipv6_gateways')
            if self.ipv6_gateways is not None:
                self.ipv6_gateways = self.ipv6_gateways.split(',')
            self.ipv6_ip = self.config['NETWORK'].get('ipv6_ip')
        elif ((self.ipv6Type is None) or (self.ipv4Type == 'DHCP') or
                (self.ipv4Type == 'USER_INPUT_REQUIRED')):
            self.ipv6_prefix = None
            self.ipv6_ip = None
            self.ipv6_gateways = None
        else:
            raise Exception('Wrong ipv6Type "{}"'.format(self.ipv6Type))

    # common method to parse hostname cfg for linux/windows spec
    def parseHostname(self):
        # parse hostname generator type
        self.hostnameType =\
            self.config['HOSTNAME'].get('hostnameGeneratorType',
                                        'VIRTUAL_MACHINE')
        if (self.hostnameType == 'VIRTUAL_MACHINE' or
           self.hostnameType == 'USER_INPUT_REQUIRED'):
            self.prefix = None
            self.fixedName = None
        elif self.hostnameType == 'PREFIX':
            self.prefix = self.config['HOSTNAME'].get('prefix')
            self.fixedName = None
        elif self.hostnameType == 'FIXED':
            self.fixedName = self.config['HOSTNAME'].get('fixedName')
            self.prefix = None
        else:
            raise Exception('Wrong hostnameGeneratorType "{}"'.format(
                            self.hostnameType))

    # common method to parse DNS cfg for linux/windows spec
    def parseDns(self):
        self.globalDnsServers = self.config['DNS'].get('dnsServers')
        if self.globalDnsServers is not None:
            self.globalDnsServers = self.globalDnsServers.split(',')
        self.globalDnsSuffixs = self.config['DNS'].get('dnsSuffixs')
        if self.globalDnsSuffixs is not None:
            self.globalDnsSuffixs = self.globalDnsSuffixs.split(',')

    def parseWinnics(self):
        self.netBiosMode = self.config['WINNICS'].get('netBiosMode')
        self.dnsServers = self.config['WINNICS'].get('dnsServers')
        if self.dnsServers is not None:
            self.dnsServers = self.dnsServers.split(',')
        self.dnsDomain = self.config['WINNICS'].get('dnsDomain')
        self.winsServers = self.config['WINNICS'].get('winsServers')
        if self.winsServers is not None:
            self.winsServers = self.winsServers.split(',')

    def parseLinuxCfg(self):
        self.config.read(self.linCfgPath)
        self.parseSpecInfo()
        self.linSpecName = self.specName
        self.parseNetwork()
        self.parseHostname()
        self.domainName = self.config['LINUXCONFIG'].get('domainName')
        self.timezone = self.config['LINUXCONFIG'].get('timezone')
        self.script_text = self.config['LINUXCONFIG'].get('script_text')
        self.parseDns()

    def parseWinCfg(self):
        self.config.read(self.winCfgPath)
        self.parseSpecInfo()
        self.winSpecName = self.specName
        self.parseNetwork()
        self.parseHostname()
        self.parseDns()
        self.rebootOption = self.config['WINCONFIG'].get('rebootOption')
        self.fullName = self.config['WINCONFIG'].get('fullName')
        self.org = self.config['WINCONFIG'].get('organization')
        self.productKey = self.config['WINCONFIG'].get('productKey')
        # parse domain or workgroup
        self.domainType =\
            self.config['WINCONFIG'].get('domainType', 'WORKGROUP')
        if self.domainType == "WORKGROUP":
            self.workgroup = self.config['WINCONFIG'].get('workgroup')
            self.domain = None
            self.domainUser = None
            self.domainPass = None
        elif self.domainType == "DOMAIN":
            self.workgroup = None
            self.domain = self.config['WINCONFIG'].get('domain')
            self.domainUser = self.config['WINCONFIG'].get('domainUser')
            self.domainPass = self.config['WINCONFIG'].get('domainPass')
        else:
            raise Exception('Wrong domainType "{}"'.format(self.domainType))
        self.autoLogon =\
            self.config['WINCONFIG'].getboolean('autoLogon', False)
        self.autoLogonCount =\
            self.config['WINCONFIG'].getint('autoLogonCount', 0)
        self.timezone = self.config['WINCONFIG'].getint('timezone', 4)
        # The local Admin password
        # ### WARNING: USE CLEAR TEXT IN winSpec.cfg AT YOUR OWN RISK!!! ###
        # Suggested to use "--win_password" command line option instead
        # It will overrid this value here
        if not self.win_password:
            self.win_password = self.config['WINCONFIG'].get('password')
        self.gui_run_once_commands =\
            self.config['WINCONFIG'].get('gui_run_once_commands')
        if self.gui_run_once_commands is not None:
            self.gui_run_once_commands = self.gui_run_once_commands.split(',')
        self.sysprepXml = self.config['WINCONFIG'].get('sysprepXml')
        self.parseWinnics()

    def listCustomizationSpecs(self):
        """
        List CustomizationSpecs present in vc server
        """
        print("------------list--------------")
        print("List Of  CustomizationSpecs:")
        list_of_specs = self.specs_svc.list()
        self.specCount = len(list_of_specs)
        pprint(list_of_specs)

    def createLinuxSpec(self):
        print("------------create 1 linux Customizationpec----------------")
        self.parseLinuxCfg()
        computerName = HostnameGenerator(prefix=self.prefix,
                                         fixed_name=self.fixedName,
                                         type=HostnameGenerator.Type(
                                             self.hostnameType))
        spec_linuxConfig = LinuxConfiguration(domain=self.domainName,
                                              hostname=computerName,
                                              time_zone=self.timezone,
                                              script_text=self.script_text)
        spec_configSpec = ConfigurationSpec(linux_config=spec_linuxConfig)
        # AdapterMapping
        ipv4Cfg = Ipv4(type=Ipv4.Type(self.ipv4Type), prefix=self.ipv4_prefix,
                       gateways=self.ipv4_gateways, ip_address=self.ipv4_ip)
        if self.ipv6Type is not None:
            ipv6addr = [Ipv6Address(prefix=self.ipv6_prefix,
                                    ip_address=self.ipv6_ip)]
            ipv6Cfg = Ipv6(gateways=self.ipv6_gateways, ipv6=ipv6addr,
                           type=Ipv6.Type(self.ipv6Type))
        else:
            ipv6Cfg = None
        ipSettings = IPSettings(windows=None, ipv4=ipv4Cfg, ipv6=ipv6Cfg)
        adapterMappingList = [AdapterMapping(adapter=ipSettings,
                                             mac_address=self.macAddress)]
        # dns_settings
        dns_settings = GlobalDNSSettings(dns_servers=self.globalDnsServers,
                                         dns_suffix_list=self.globalDnsSuffixs)
        # CreateSpec
        linspec_spec = CustomizationSpec(configuration_spec=spec_configSpec,
                                         interfaces=adapterMappingList,
                                         global_dns_settings=dns_settings)
        lin_create_spec = self.specs_svc.CreateSpec(name=self.specName,
                                                    description=self.specDesc,
                                                    spec=linspec_spec)
        # svc Create
        self.specs_svc.create(spec=lin_create_spec)
        # append it to existing list, for delete and cleanup
        self.specsAdded.append(self.specName)
        # list after create
        self.listCustomizationSpecs()
        print("----------------------------")

    def createWinSpec(self):
        print("------------create 1 windows CustomizationSpec----------------")
        self.parseWinCfg()
        # IPSettings
        ipv4Cfg = Ipv4(type=Ipv4.Type(self.ipv4Type), prefix=self.ipv4_prefix,
                       gateways=self.ipv4_gateways, ip_address=self.ipv4_ip)
        if self.ipv6Type is not None:
            ipv6addr = [Ipv6Address(prefix=self.ipv6_prefix,
                                    ip_address=self.ipv6_ip)]
            ipv6Cfg = Ipv6(gateways=self.ipv6_gateways, ipv6=ipv6addr,
                           type=Ipv6.Type(self.ipv6Type))
        else:
            ipv6Cfg = None
        windowsNicSettings = WindowsNetworkAdapterSettings(
            net_bios_mode=self.netBiosMode, dns_servers=self.dnsServers,
            dns_domain=self.dnsDomain, wins_servers=self.winsServers)
        ipSettings = IPSettings(windows=windowsNicSettings,
                                ipv4=ipv4Cfg, ipv6=ipv6Cfg)
        # AdapterMapping
        adapterMappingList = [AdapterMapping(adapter=ipSettings,
                                             mac_address=self.macAddress)]

        # WindowsConfiguration
        myReboot = WindowsConfiguration.RebootOption(self.rebootOption)
        computerName = HostnameGenerator(prefix=self.prefix,
                                         fixed_name=self.fixedName,
                                         type=HostnameGenerator.Type(
                                             self.hostnameType))
        userData = UserData(computer_name=computerName,
                            product_key=self.productKey,
                            full_name=self.fullName,
                            organization=self.org)
        myDomain = Domain(domain=self.domain, workgroup=self.workgroup,
                          domain_username=self.domainUser,
                          domain_password=self.domainPass,
                          type=Domain.Type(self.domainType))
        guiUnattended = GuiUnattended(auto_logon_count=self.autoLogonCount,
                                      auto_logon=self.autoLogon,
                                      time_zone=self.timezone,
                                      password=self.win_password)
        mySysprep = WindowsSysprep(domain=myDomain,
                                   gui_unattended=guiUnattended,
                                   user_data=userData,
                                   gui_run_once_commands=self.
                                   gui_run_once_commands)
        winCfg = WindowsConfiguration(reboot=myReboot,
                                      sysprep=mySysprep,
                                      sysprep_xml=self.sysprepXml)
        # CustomizationSpec
        spec_configSpec = ConfigurationSpec(windows_config=winCfg)
        dns_settings = GlobalDNSSettings(dns_servers=self.globalDnsServers,
                                         dns_suffix_list=self.globalDnsSuffixs)
        winspec_spec = CustomizationSpec(configuration_spec=spec_configSpec,
                                         interfaces=adapterMappingList,
                                         global_dns_settings=dns_settings)
        # CreateSpec
        win_create_spec = self.specs_svc.CreateSpec(name=self.specName,
                                                    description=self.specDesc,
                                                    spec=winspec_spec)
        # list before create
        self.listCustomizationSpecs()
        existingSpecCount = self.specCount
        # svc Create
        self.specs_svc.create(spec=win_create_spec)
        # append it to existing list, for delete and cleanup
        self.specsAdded.append(self.specName)
        # list after create
        self.listCustomizationSpecs()
        print("----------------------------")
        newSpecCount = self.specCount
        if (newSpecCount != existingSpecCount + 1):
            raise Exception('Error createSpec due to spec count={}'.
                            format(newSpecCount))

    def getSetSpec(self):
        print("-----------Get existing Spec------------")
        # Get created specs, modify timezone and description of the linSpec
        linSpec = self.specs_svc.get(self.linSpecName)
        pprint(linSpec)
        winSpec = self.specs_svc.get(self.winSpecName)
        pprint(winSpec)
        linSpec.spec.spec.configuration_spec.linux_config.time_zone =\
            'Europe/London'
        linSpec.spec.description = linSpec.spec.description +\
            " modified by vapi set() method"
        print("-----------Set to modify existing linSpec------------")
        self.specs_svc.set(name=self.linSpecName, spec=linSpec.spec)
        # Now check again if its timezone and description has changed
        print("-----------Get the modified linSpec------------")
        linSpec = self.specs_svc.get(self.linSpecName)
        pprint(linSpec)
        print("----------------------------")

    def deleteSpec(self):
        print("-----------Delete created spec for cleanup------------")
        print("-----------before delete------------")
        self.listCustomizationSpecs()
        existingSpecCount = self.specCount
        for specName in self.specsAdded:
            self.specs_svc.delete(specName)
            existingSpecCount -= 1
        # list again, there should be []
        print("-----------after delete------------")
        self.listCustomizationSpecs()
        newSpecCount = self.specCount
        print("----------------------------")
        if (newSpecCount != existingSpecCount):
            raise Exception('Error deleteSpec due to current specCount {}!={}'.
                            format(newSpecCount, existingSpecCount))


def main():
    myCustSpecMgr = CustomizationSpecManager()
    myCustSpecMgr.listCustomizationSpecs()
    myCustSpecMgr.createLinuxSpec()
    myCustSpecMgr.createWinSpec()
    myCustSpecMgr.getSetSpec()
    myCustSpecMgr.deleteSpec()


if __name__ == '__main__':
    main()
