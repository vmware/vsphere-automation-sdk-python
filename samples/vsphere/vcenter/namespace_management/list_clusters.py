#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0.1+'

from com.vmware.vcenter.namespace_management_client import Clusters

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration
from pprint import pprint


class ListCluster(object):
    """
    Demonstrates getting list of WCP enabled clusters
    Sample Prerequisites:
    vCenter/ESX with wcp enable"
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.list_cluster = Clusters(stub_config)

    def run(self):
        """
        List cluster present in server
        """
        clusters = self.list_cluster
        list_of_cl = clusters.list()
        print("----------------------------")
        print("List Of clusters")
        print("----------------------------")
        pprint(list_of_cl)
        print("----------------------------")


def main():
    list_cl = ListCluster()
    list_cl.run()


if __name__ == '__main__':
    main()
