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
    Demonstrates getting list of project/vpc/subnet present in vCenter

    Prerequisites:
        - Projects/VPCs/Subnets created
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Connect to vSphere client
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def listAll(self):
        print("============== List all projects, VPCs, and subnets ===============")
        network = self.client.vcenter.network
        projResult = network.Projects.list()
        for projectInfo in projResult.projects:
            print(projectInfo.project.id)

            vpcsResult = network.projects.Vpcs.list(projectInfo.project.id)
            for vpcInfo in vpcsResult.vpcs:
                print("  " + vpcInfo.vpc.id)

                subnetMo = network.projects.vpcs.Subnets
                projId = projectInfo.project.id
                vpcId = vpcInfo.vpc.id
                subnetResult = subnetMo.list(projId, vpcId)
                for subnetInfo in subnetResult.subnets:
                    print("    " + subnetInfo.subnet.id)


def main():
    svc = VpcSvc()
    svc.listAll()


if __name__ == '__main__':
    main()
