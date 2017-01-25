"""
* *******************************************************
* Copyright (c) VMware, Inc. 2014. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2014 VMware, Inc. All rights reserved.'

import argparse
from samples.vsphere.common.lookup_service_helper import LookupServiceHelper


class PrintServices(object):
    """
    Demonstrates service discovery using lookup service APIs.
    The sample prints all the PSC (Platform Service Controller) and Management Node (vCenter Server) and
    some of the critical services (SSO, VAPI, VIM etc.) running on these nodes. This sample can also be used
    to find out the server deployment (e.g. MxN setup with multiple PSC/Management nodes).
    """

    def __init__(self):
        self.lswsdlurl = None
        self.lssoapurl = None

    def options(self):
        self.argparser = argparse.ArgumentParser(description=self.__doc__)
        # setup the argument parser
        self.argparser.add_argument('-w', '--lswsdlurl',
                                    help='Lookup service WSDL URL')
        self.argparser.add_argument('-s', '--lssoapurl',
                                    help='Lookup service SOAP URL')
        self.argparser.add_argument('-v', '--skipverification',
                                    action='store_true',
                                    help='Do not verify server certificate')
        self.args = self.argparser.parse_args()   # parse all the sample arguments when they are all set

    def setup(self):
        self.lswsdlurl = self.args.lswsdlurl
        assert self.lswsdlurl is not None
        print('lswsdlurl: {0}'.format(self.lswsdlurl))

        self.lssoapurl = self.args.lssoapurl
        assert self.lssoapurl is not None
        print('lssoapurl: {0}'.format(self.lssoapurl))

        self.skip_verification = self.args.skipverification

    def execute(self):
        print('Connecting to lookup service url: {0}'.format(self.lssoapurl))
        lookupservicehelper = LookupServiceHelper(wsdl_url=self.lswsdlurl,
                                                  soap_url=self.lssoapurl,
                                                  skip_verification=self.skip_verification)
        lookupservicehelper.connect()

        # print the PSC nodes and SSO service endpoint URLs
        for index, sso_url in enumerate(lookupservicehelper.find_sso_urls(), start=1):
            print('=============================')
            print('PSC node: {0}'.format(index))
            print('    SSO URL: {0}'.format(sso_url))
            print('=============================')

        # print the mgmt (vCenter Server) nodes and some of the critical service endpoint URLs
        for instance_name, node_id in lookupservicehelper.find_mgmt_nodes().items():
            print('=============================')
            print('Mgmt node instance name: {0} node_id: {1}'.format(instance_name, node_id))
            print('    VAPI URL: {0}'.format(lookupservicehelper.find_vapi_url(node_id)))
            print('    VIM URL: {0}'.format(lookupservicehelper.find_vim_url(node_id)))
            print('    SPBM URL: {0}'.format(lookupservicehelper.find_vim_pbm_url(node_id)))
            print('=============================')

    def cleanup(self):
        pass


def main():
    printServices = PrintServices()
    printServices.options()
    printServices.setup()
    printServices.execute()
    printServices.cleanup()

# Start program
if __name__ == "__main__":
    main()