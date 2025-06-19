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


class VpcSvc(object):
    """
    Demonstrates get/list of vpc

    Prerequisites:
        - Projects/VPCs/Subnets created
    """
    def __init__(self):
        self.proj_id = None
        self.vpc_id = None
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
        parser.add_argument('-i', '--ids',
                            action='store',
                            help='Ids of the vpcs')
        parser.add_argument('-n', '--names',
                            action='store',
                            help='names of the vpcs')
        parser.add_argument('-e', '--external_ids',
                            action='store',
                            help='external ids of the vpcs')
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

        # Connect to vSphere client
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def listVpc(self):
        print("\n============== List VPCs =============================")
        filterSpec = self.client.vcenter.network.projects.Vpcs.FilterSpec()
        filterSpec.ids = self.ids
        filterSpec.names = self.names
        filterSpec.external_ids = self.external_ids

        vpcs = self.client.vcenter.network.projects.Vpcs.list(
                                                             self.proj_id,
                                                             filterSpec)
        print(vpcs)

    def getVpc(self):
        print("\n============== Get One Vpc ================================")
        vpc = self.client.vcenter.network.projects.Vpcs.get(
                                                           self.proj_id,
                                                           self.vpc_id)
        print(vpc)


def main():
    svc = VpcSvc()

    if svc.method == 'list':
        svc.listVpc()
    elif svc.method == 'get':
        svc.getVpc()
    else:
        print("unknown method: " + svc.method)


if __name__ == '__main__':
    main()
