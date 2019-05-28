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

import requests


from com.vmware.vcenter.topology_client import Pscs

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session

from vmware.vapi.lib.connect import get_connector, get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.core import ApplicationContext
from vmware.vapi.lib.constants import SHOW_UNRELEASED_APIS


class SampleDecommission(object):
    """
     Demonstrates Decommission operation for external PSC
     Sample Prerequisites:
     Embedded vCenter on linux platform with replication to Platform Services
     Controller to be decommissioned
     """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument(
            '-psc_h', '--psc_host_name', action='store',
            default='Sample_PSC_hostname',
            help='Platform Services Controller FQDN / IP as per configuration')
        parser.add_argument(
            '-a', '--sso_admin_username', action='store',
            default='Sample_PSC_username',
            help='Platform Services Controller admin username')
        parser.add_argument(
            '-w', '--sso_admin_password', action='store',
            default='Sample_PSC_Admin_Password',
            help='Platform Services Controller admin password')

        args = sample_util.process_cli_args(parser.parse_args())
        self.psc_hostname = args.psc_host_name
        self.username = args.username
        self.password = args.password
        self.sso_admin_username = args.sso_admin_username
        self.sso_admin_password = args.sso_admin_password
        self.server = args.server
        self.skipverification = args.skipverification

    def run(self):
        """
         Decommissions a PSC node from a Management Node
         """
        session = get_unverified_session() if self.skipverification else None

        sec_ctx = create_user_password_security_context(
                    self.username, self.password)
        # TODO The following line to be deleted when API is changed to
        #  @Release type. As of now this is only for testing
        app_ctx = ApplicationContext({SHOW_UNRELEASED_APIS: "True"})

        connector = get_requests_connector(
            session=session,
            msg_protocol='json',
            url='https://{0}:5480/api'.format(self.server))
        connector.set_security_context(sec_ctx)
        connector.set_application_context(app_ctx)
        stub_config = StubConfigurationFactory.new_std_configuration(connector)
        pscs_obj = Pscs(stub_config)
        """
         Running decommission task precheck.
         Remove the line ", only_precheck = True" to perform decommission.
         """
        decommission_task = pscs_obj.decommission_task(
            self.psc_hostname,
            Pscs.DecommissionSpec(
            sso_admin_username=self.sso_admin_username,
            sso_admin_password=self.sso_admin_password),
            only_precheck=True)

        print(
            'Decommission operation started with task ID: \n%s',
            decommission_task.get_task_id())


def main():
    """
     Entry point for the sample client
     """
    decommision_obj = SampleDecommission()
    decommision_obj.run()


if __name__ == '__main__':
    main()
