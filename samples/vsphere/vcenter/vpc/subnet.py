#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.


__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '9.0+'

from vmware.vapi.vsphere.client import create_vsphere_client  # noqa: E402
from samples.vsphere.common import sample_cli   # noqa: E402
from samples.vsphere.common import sample_util  # noqa: E402
from samples.vsphere.common.ssl_helper import get_unverified_session   # noqa: E402


class SubnetSvc(object):
    """
    Demonstrates get/list of subnet

    Prerequisites:
        - Projects/VPCs/Subnets created
    """
    def __init__(self):
        self.proj_id = None
        self.vpc_id = None
        self.subnet_id = None
        self.ids = None
        self.names = None
        self.external_ids = None
        self.method = None

        parser = sample_cli.build_arg_parser()
        parser.add_argument('-x', '--proj_id',
                            action='store',
                            help='Id of the project')
        parser.add_argument('-y', '--vpc_id',
                            action='store',
                            help='Id of the vpc')
        parser.add_argument('-z', '--subnet_id',
                            action='store',
                            help='Id of the subnet')
        parser.add_argument('-i', '--ids',
                            action='store',
                            help='Ids of the subnets')
        parser.add_argument('-n', '--names',
                            action='store',
                            help='names of the subnets')
        parser.add_argument('-e', '--external_ids',
                            action='store',
                            help='external ids of the subnets')
        parser.add_argument('-m', '--method',
                            action='store',
                            help='get or list')
        args = sample_util.process_cli_args(parser.parse_args())

        if args.ids:
            self.ids = set(args.ids.split(','))
        if args.names:
            self.names = set(args.names.split(','))
        if args.external_ids:
            self.external_ids = set(args.external_ids.split(','))
        self.method = args.method
        self.proj_id = args.proj_id
        self.vpc_id = args.vpc_id
        self.subnet_id = args.subnet_id

        # Connect to vSphere client
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def listSubnet(self):
        print("\n============== List Subnets ==========================")
        network = self.client.vcenter.network
        filterSpec = network.projects.vpcs.Subnets.FilterSpec()
        filterSpec.ids = self.ids
        filterSpec.names = self.names
        filterSpec.external_ids = self.external_ids

        subnets = self.client.vcenter.network.projects.vpcs.Subnets.list(
                                                                  self.proj_id,
                                                                  self.vpc_id,
                                                                  filterSpec)
        print(subnets)

    def getSubnet(self):
        print("\n============== Get One Subnet =============================")
        subnet = self.client.vcenter.network.projects.vpcs.Subnets.get(
                                                                self.proj_id,
                                                                self.vpc_id,
                                                                self.subnet_id)
        print(subnet)


def main():
    svc = SubnetSvc()

    if svc.method == 'list':
        svc.listSubnet()
    elif svc.method == 'get':
        svc.getSubnet()
    else:
        print("unknown method: " + svc.method)


if __name__ == '__main__':
    main()
