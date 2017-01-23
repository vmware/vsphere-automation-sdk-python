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
from samples.vsphere.common.sample_config import SampleConfig
from samples.vsphere.common.lookup_service_helper import LookupServiceHelper
from samples.vsphere.common.logging_context import LoggingContext

logger = LoggingContext.get_logger('samples.vsphere.lookupservice.print_services')


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
        self.argparser.add_argument('-lswsdlurl', '--lswsdlurl', help='Lookup service WSDL URL')
        self.argparser.add_argument('-lssoapurl', '--lssoapurl', help='Lookup service SOAP URL')
        self.args = self.argparser.parse_args()   # parse all the sample arguments when they are all set

    def setup(self):
        if self.args.lswsdlurl is None:
            self.lswsdlurl = SampleConfig.get_ls_wsdl_url()  # look for lookup service WSDL in the sample config
        else:
            self.lswsdlurl = self.args.lswsdlurl
        assert self.lswsdlurl is not None
        logger.info('lswsdlurl: {0}'.format(self.lswsdlurl))

        if self.args.lssoapurl is None:
            self.lssoapurl = SampleConfig.get_ls_soap_url()  # look for lookup service SOAP URL in the sample config
        else:
            self.lssoapurl = self.args.lssoapurl
        assert self.lssoapurl is not None
        logger.info('lssoapurl: {0}'.format(self.lssoapurl))

    def execute(self):
        logger.info('Connecting to lookup service url: {0}'.format(self.lssoapurl))
        lookupservicehelper = LookupServiceHelper(wsdl_url=self.lswsdlurl, soap_url=self.lssoapurl)
        lookupservicehelper.connect()

        # print the PSC nodes and SSO service endpoint URLs
        for index, sso_url in enumerate(lookupservicehelper.find_sso_urls(), start=1):
            logger.info('=============================')
            logger.info('PSC node: {0}'.format(index))
            logger.info('    SSO URL: {0}'.format(sso_url))
            logger.info('=============================')

        # print the mgmt (vCenter Server) nodes and some of the critical service endpoint URLs
        for instance_name, node_id in lookupservicehelper.find_mgmt_nodes().items():
            logger.info('=============================')
            logger.info('Mgmt node instance name: {0} node_id: {1}'.format(instance_name, node_id))
            logger.info('    VAPI URL: {0}'.format(lookupservicehelper.find_vapi_url(node_id)))
            logger.info('    VIM URL: {0}'.format(lookupservicehelper.find_vim_url(node_id)))
            logger.info('    SPBM URL: {0}'.format(lookupservicehelper.find_vim_pbm_url(node_id)))
            logger.info('=============================')

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