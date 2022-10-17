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
__vcenter_version__ = '8.0.0+'

from com.vmware.vcenter.namespace_management.supervisors_client import Summary
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration


class GetSupervisorsSummary(object):
    """
    Demonstrates looking up a Supervisor Summary on a given Supervisor Cluster.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('--supervisor',
                            required=True,
                            help='The MoID of the Supervisor to query.')

        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
            args.server, args.username, args.password,
            session)
        self.supervisor_summary = Summary(stub_config)
        self.supervisor = args.supervisor

    def run(self):
        """
        Get Supervisor Summary on vCenter Server.
        """
        summary = self.supervisor_summary.get(self.supervisor)
        print('name: {0}'.format(summary.name))
        print('config_status: {0}'.format(summary.config_status))
        print('kubernetes_status: {0}'.format(summary.kubernetes_status))
        print('stats: {0}\n'.format(summary.stats))


def main():
    list_cl = GetSupervisorsSummary()
    list_cl.run()


if __name__ == '__main__':
    main()
