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
__vcenter_version__ = '7.0+'

import random
import time

from com.vmware.vstats_client import Providers, AcqSpecs, CidMid, RsrcId, Data

from samples.vsphere.common import sample_util
from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.vcenter.vstats.helpers.sample_cli import parser


class SampleQueryDataPointsPredicate(object):
    """
    Description: Demonstrates querying data points filtered by cid
    by creating Acquisition Specification using Query
    Predicate "ALL".
    Sample Prerequisites:
    vCenter 7.0x with 7.0x ESXi hosts.
    """

    def __init__(self):
        args = sample_util.process_cli_args(parser.parse_args())
        self.interval = int(args.interval)
        self.expiration = int(args.expiration)

        stub_config = get_configuration(
                args.server, args.username, args.password,
                args.skipverification)
        self.acq_specs_client = AcqSpecs(stub_config)
        self.data_client = Data(stub_config)
        self.providers_client = Providers(stub_config)

    def run(self):
        cid = "disk.throughput.usage.VM"
        wait_time = 30
        vm_type = "VM"
        host_type = "HOST"
        memo = "user definition of acquisition spec"

        cid_mid_obj = CidMid(cid=cid)
        counter_spec_obj = self.acq_specs_client.CounterSpec(
                cid_mid=cid_mid_obj)

        # To collect stats data from all VMs on a particular host, provide
        # QueryPredicate "ALL" for VM resourceId.
        rsrc_obj1 = RsrcId(id_value="", type=vm_type, predicate="ALL")

        # Choose a random host.
        providers = self.providers_client.list()
        random_host_id = random.choice(providers).id_value

        rsrc_obj2 = RsrcId(id_value=random_host_id, type=host_type)

        # Create an Acquisition Specification to collect stats data from all
        # VMs on a host using QueryPredicate "ALL".
        acq_spec_obj = self.acq_specs_client.CreateSpec(
                counters=counter_spec_obj,
                resources=[rsrc_obj1, rsrc_obj2],
                interval=self.interval,
                expiration=self.expiration,
                memo_=memo
        )
        acq_spec_id = self.acq_specs_client.create(acq_spec_obj)
        SampleQueryDataPointsPredicate.print_output(
                "Acquisition Specification created with ID: " + acq_spec_id)

        # Get the Acquisition Specification.
        acq_spec_info = self.acq_specs_client.get(acq_spec_id)
        SampleQueryDataPointsPredicate.print_output(
                "Details of Acquisition Specification with ID: " + acq_spec_id,
                acq_spec_info)

        # Wait for 30 seconds for data collection to happen.
        time.sleep(wait_time)

        # Query for data points filtered by cid.
        filter_spec = self.data_client.FilterSpec(cid=cid)
        data_points = self.data_client.query_data_points(filter=filter_spec)
        SampleQueryDataPointsPredicate.print_output(
                "Data points collected", data_points)

        # CleanUp.
        # Delete the Acquisition Specification.
        self.acq_specs_client.delete(acq_spec_id)
        SampleQueryDataPointsPredicate.print_output(
                "Acquisition Specification with ID: " + acq_spec_id +
                " is deleted")

    @staticmethod
    def print_output(*argv):
        print("------------------------------------")
        for arg in argv:
            print(arg)


def main():
    """
     Entry point for the sample client.
    """
    query_dp = SampleQueryDataPointsPredicate()
    query_dp.run()


if __name__ == '__main__':
    main()
