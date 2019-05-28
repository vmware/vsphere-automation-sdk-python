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

import os
import requests

from com.vmware.vcenter.system_config_client import DeploymentType

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session

from vmware.vapi.core import ApplicationContext
from vmware.vapi.lib.constants import SHOW_UNRELEASED_APIS
from vmware.vapi.lib.connect import get_connector, get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter, ApiProviderFilter
from vmware.vapi.security.user_password import \
    create_user_password_security_context


class SampleConverge(object):
    """
     Sample demonstrating vCenter External to Embedded Convergence operation
     Sample Prerequisites:
     vCenter on linux platform with external Platform Services Controller
     """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument(
            '-a', '--sso_admin_username', action='store', required=True,
            default='Sample_PSC_username',
            help='Platform Services Controller admin username')
        parser.add_argument(
            '-w', '--sso_admin_password', action='store', required=True,
            default='Sample_PSC_Admin_Password',
            help='Platform Services Controller admin password')

        args = sample_util.process_cli_args(parser.parse_args())
        self.username = args.username
        self.password = args.password
        self.sso_admin_username = args.sso_admin_username
        self.sso_admin_password = args.sso_admin_password
        self.server = args.server
        self.skipverification = args.skipverification

    def run(self):
        """
         Converges the external PSC into the Management Node without shutting
         down the Platform Services Controller.
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
                url='https://{0}:5480/api'.format(self.server),
                provider_filter_chain=[
                    LegacySecurityContextFilter(
                        security_context=sec_ctx)])
        connector.set_application_context(app_ctx)
        stub_config = StubConfigurationFactory.new_std_configuration(connector)
        deployment_type = DeploymentType(stub_config)
        """
         Running convergence task precheck.
         Remove the line ", only_precheck = True" to perform convergence.
         """
        convergence_task = deployment_type.convert_to_vcsa_embedded_task(
            DeploymentType.ConvergenceSpec(DeploymentType.PscInfo(
                sso_admin_username=self.sso_admin_username,
                sso_admin_password=self.sso_admin_password),
                only_precheck=True))

        print('Converge operation started with task ID: \n{0}'.format(
            convergence_task.get_task_id()))


def main():
    """
     Entry point for the sample client
    """
    converge = SampleConverge()
    converge.run()


if __name__ == '__main__':
    main()
