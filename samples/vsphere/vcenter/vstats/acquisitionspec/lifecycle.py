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

from com.vmware.vstats_client import Providers, AcqSpecs, CidMid, RsrcId

from samples.vsphere.common import sample_util
from samples.vsphere.vcenter.hcl.utils import get_configuration
from samples.vsphere.vcenter.vstats.helpers.sample_cli import parser


class SampleAcquisitionSpecLifecycle(object):
    """
    Demonstrates create, get, list, update and delete operations of
    Acquisition Specifications.
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
        self.providers_client = Providers(stub_config)
        self.acq_specs_client = AcqSpecs(stub_config)

    def run(self):
        cid = "cpu.capacity.demand.HOST"
        new_cid = "mem.capacity.usage.HOST"
        host_type = "HOST"
        memo = "user definition of acquisition spec"

        # The counter and associated resources can be chosen using discovery
        # APIs. Please refer to samples in discovery package to obtain this
        # metadata. In this sample, we create an Acquisition
        # Specification for a HOST counter.
        cid_mid_obj = CidMid(cid=cid)
        counter_spec_obj = self.acq_specs_client.CounterSpec(
                cid_mid=cid_mid_obj)

        # Choose a random host from which stats data needs to be collected.
        providers = self.providers_client.list()
        random_host_id = random.choice(providers).id_value
        host_resource_id_obj = RsrcId(id_value=random_host_id,
                                      type=host_type)
        acq_spec_obj = self.acq_specs_client.CreateSpec(
                counters=counter_spec_obj,
                resources=[host_resource_id_obj],
                interval=self.interval,
                expiration=self.expiration,
                memo_=memo
        )

        # Create an Acquisition Specification.
        acq_spec_id = self.acq_specs_client.create(acq_spec_obj)
        SampleAcquisitionSpecLifecycle.print_output(
                "Acquisition Specification created with ID: " + acq_spec_id)

        # List Acquisition Specifications.
        SampleAcquisitionSpecLifecycle.print_output(
                "List of Acquisition Specifications",
                self.acq_specs_client.list())

        # Update the existing Acquisition Specification by only modifying the
        # intended field in UpdateSpec, keeping all other fields as it is.
        cid_mid_obj = CidMid(cid=new_cid)
        counter_spec_obj = self.acq_specs_client.CounterSpec(
                cid_mid=cid_mid_obj)
        updated_acq_spec_obj = self.acq_specs_client.UpdateSpec(
                counters=counter_spec_obj,
                resources=[host_resource_id_obj],
                interval=self.interval,
                expiration=self.expiration,
                memo_=memo
        )
        self.acq_specs_client.update(acq_spec_id, updated_acq_spec_obj)
        SampleAcquisitionSpecLifecycle.print_output(
                "Updated Acquisition Specification",
                self.acq_specs_client.get(acq_spec_id))

        # Get the Acquisition Specification.
        acq_spec_info = self.acq_specs_client.get(acq_spec_id)
        SampleAcquisitionSpecLifecycle.print_output(
                "Details of Acquisition Specification with ID " + acq_spec_id,
                acq_spec_info)

        # Delete Acquisition Specification.
        self.acq_specs_client.delete(acq_spec_id)
        SampleAcquisitionSpecLifecycle.print_output(
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
    sample_acq_spec_lifecycle_obj = SampleAcquisitionSpecLifecycle()
    sample_acq_spec_lifecycle_obj.run()


if __name__ == '__main__':
    main()
