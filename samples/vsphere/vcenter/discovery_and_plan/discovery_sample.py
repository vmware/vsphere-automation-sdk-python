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
__vcenter_version__ = '7.0+'

from com.vmware.vcenter.lcm.discovery_client import ProductCatalog, AssociatedProducts

from samples.vsphere.common import sample_cli, sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.hcl.utils import get_configuration


class SampleDiscovery(object):
    """
     Sample demonstrating vCenter LCM Discovery APIs
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.product_client = ProductCatalog(stub_config)
        self.associated_products_client = AssociatedProducts(stub_config)

    def run(self):
        """
        Access the Discovery APIs to list available products and associated products
        """
        # Product Catlog
        product_catlog = self.product_client.list()
        print("Product Catlog list: \n", product_catlog)

        # Associated Products
        associated_products = self.associated_products_client.list()
        print("Associated Products list : \n", associated_products)

        # Add product
        spec = {'product_name': 'VMware Identity Manager', 'version': '3.3', 'deployments': '3'}
        add_associated_product = self.associated_products_client.create(spec)
        print('Added new product. \n', add_associated_product)

        associated_products = self.associated_products_client.list()
        print("Associated Products after adding the product: \n", associated_products)

        # Update product
        update_spec = {'deployments': '9'}
        update_associated_product = self.associated_products_client.update(add_associated_product, update_spec)
        associated_products = self.associated_products_client.list()
        print("Associated Products after updating the product: \n", associated_products)

        # Delete product
        delete_associated_product = self.associated_products_client.delete(add_associated_product)
        associated_products = self.associated_products_client.list()
        print("Associated Products after deleting the product: \n{0}", associated_products)


def main():
    """
     Entry point for the sample client
    """
    discovery = SampleDiscovery()
    discovery.run()


if __name__ == '__main__':
    main()
