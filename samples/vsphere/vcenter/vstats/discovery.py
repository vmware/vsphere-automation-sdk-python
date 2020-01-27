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

from com.vmware.vstats_client import Counters, Providers, ResourceTypes, \
        CounterMetadata, Metrics, CounterSets, ResourceAddressSchemas

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.vcenter.hcl.utils import get_configuration


class SampleDiscovery(object):
    """
    Description: Demonstrates all vSphere Stats discovery APIs which
    give current state of the system.
    Sample Prerequisites:
    vCenter 7.0x with 7.0x ESXi hosts.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        stub_config = get_configuration(
                args.server, args.username, args.password,
                args.skipverification)
        self.counters_client = Counters(stub_config)
        self.providers_client = Providers(stub_config)
        self.resource_types_client = ResourceTypes(stub_config)
        self.counter_metadata_client = CounterMetadata(stub_config)
        self.metrics_client = Metrics(stub_config)
        self.counter_sets_client = CounterSets(stub_config)
        self.resource_address_schemas_client = ResourceAddressSchemas(
                stub_config)

    def run(self):
        """
        Access the Discovery APIs to
        List - counters, countermetadata, providers, resource types,
               metrics, counter sets.
        Get - resource address schema.
        """
        # Counters List.
        counters = self.counters_client.list()
        SampleDiscovery.print_output("Counters List", counters)

        # Choose a random counter and provide cid as input to
        # list CounterMetaData.
        random_cid = random.choice(counters).cid
        # List of counter metadata associated with that counter.
        counter_metadata = self.counter_metadata_client.list(random_cid)
        SampleDiscovery.print_output("Counter Metadata List", counter_metadata)

        # Choose a random counter and provide resource_address_schema_id as
        # input to get Resource Address Schema.
        random_resource_address_schema_id = random.choice(counters).\
            resource_address_schema
        # Get resource address schema associated with that counter.
        resource_address_schema = self.resource_address_schemas_client.get(
                random_resource_address_schema_id)
        SampleDiscovery.print_output("Resource Address Schema",
                                     resource_address_schema)

        # List of vSphere Stats providers connected to vCenter Server.
        providers = self.providers_client.list()
        SampleDiscovery.print_output("Providers List", providers)

        # List of resource types supported by vSphere Stats.
        resource_types = self.resource_types_client.list()
        SampleDiscovery.print_output("Resource Types List", resource_types)

        # List of metrics supported by vSphere Stats.
        metrics = self.metrics_client.list()
        SampleDiscovery.print_output("Metrics List", metrics)

        # List of vSphere Stats defined Counter-sets.
        counter_sets = self.counter_sets_client.list()
        SampleDiscovery.print_output("Counter Sets List", counter_sets)

    @staticmethod
    def print_output(*argv):
        print("------------------------------------")
        for arg in argv:
            print(arg)


def main():
    """
     Entry point for the sample client.
    """
    discovery = SampleDiscovery()
    discovery.run()


if __name__ == '__main__':
    main()
