#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2022. All Rights Reserved.
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
__copyright__ = 'Copyright 2022 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0.2+'

from com.vmware.vcenter.namespace_management.supervisor_services_client import \
    ClusterSupervisorServices, Versions

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration

separator = '-' * 40


class ListClusterSupervisorServices(object):
    """
    Demonstrates looking up a list of Supervisor Services installed on a given
    Supervisor Cluster.
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('--cluster',
                    required=True,
                    help='The MoID of the Supervisor Cluster to query.')

        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.cluster_supervisor_services = ClusterSupervisorServices(
            stub_config)
        self.versions = Versions(stub_config)
        self.cluster = args.cluster

    def run(self):
        """
        List Supervisor Services registered on vCenter Server.
        """
        services = self.cluster_supervisor_services.list(self.cluster)
        print('{0}\nList of Cluster Supervisor Services\n{0}'.format(separator))
        for s in services:
            info = self.versions.get(s.supervisor_service, s.current_version)
            print('Service:         {0}'.format(s.supervisor_service))
            print('Display Name:    {0}'.format(info.display_name))
            print('Content Type:    {0}'.format(info.content_type))
            print('Current Version: {0}'.format(s.current_version))
            print('Desired Version: {0}'.format(s.desired_version))
            print('Config Status:   {0}\n{1}'.format(s.config_status,
                separator))


def main():
    list_cl = ListClusterSupervisorServices()
    list_cl.run()


if __name__ == '__main__':
    main()
