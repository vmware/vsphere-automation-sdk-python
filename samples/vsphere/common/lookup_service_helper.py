"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013. All Rights Reserved.
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
__copyright__ = 'Copyright 2013 VMware, Inc. All rights reserved.'

import os
from suds.client import Client


class LookupServiceHelper(object):
    def __init__(self, wsdl_url, soap_url, skip_verification):
        self.wsdl_url = wsdl_url
        self.soap_url = soap_url
        self.skip_verification = skip_verification
        self.client = None
        self.managedObjectReference = None
        self.serviceRegistration = None

    def connect(self):
        if self.client is None:
            # Suds library doesn't support passing unverified context to disable
            # server certificate verification. Thus disable checking globally in
            # order to skip verification. This is not recommended in production
            # code. see https://www.python.org/dev/peps/pep-0476/
            if self.skip_verification:
                import ssl
                try:
                    _create_unverified_https_context = \
                        ssl._create_unverified_context
                except AttributeError:
                    # Legacy Python that doesn't verify HTTPS certificates by
                    # default
                    pass
                else:
                    # Handle target environment that doesn't support HTTPS
                    # verification
                    ssl._create_default_https_context = \
                        _create_unverified_https_context

            self.client = Client(url=self.wsdl_url, location=self.soap_url)
            assert self.client is not None
            self.client.set_options(service='LsService', port='LsPort')

        self.managedObjectReference = self.client.factory.create(
            'ns0:ManagedObjectReference')
        self.managedObjectReference._type = 'LookupServiceInstance'
        self.managedObjectReference.value = 'ServiceInstance'

        lookupServiceContent = self.client.service.RetrieveServiceContent(
            self.managedObjectReference)

        self.serviceRegistration = lookupServiceContent.serviceRegistration

    def find_sso_urls(self):
        """
        Finds all the SSO service URLs.
        In an MxN setup where there are more than one infrastructure node; This method returns more than one URL.

        :rtype: list
        :return: list of SSO Service endpoint URLs
        """
        return self.__find_platform_service_urls(product='com.vmware.cis',
                                                 service='cs.identity',
                                                 endpoint='com.vmware.cis.cs.identity.sso',
                                                 protocol='wsTrust')

    def find_sso_url(self):
        """
        Finds the SSO service URL.
        In an MxN setup where there are more than one infrastructure node; This method returns the first SSO service endpoint URL
        as returned by the lookup service.

        :rtype: :class:`str`
        :return: SSO Service endpoint URL
        """
        result = self.__find_platform_service_urls(product='com.vmware.cis',
                                                   service='cs.identity',
                                                   endpoint='com.vmware.cis.cs.identity.sso',
                                                   protocol='wsTrust')
        return result[0]

    def find_vapi_urls(self):
        """
        Finds all the vAPI service endpoint URLs.
        In an MxN setup where there are more than one management node; this method returns more than one URL.

        :rtype: dictionary
        :return: vapi service endpoint URLs in a dictionary where the key is the node_id and the value is the service URL
        """
        return self.__find_service_urls(product='com.vmware.cis',
                                        service='cs.vapi',
                                        endpoint='com.vmware.vapi.endpoint',
                                        protocol='vapi.json.https.public')

    def find_vapi_url(self, node_id):
        """
        Finds the vapi service endpoint URL of a management node

        :type: :class:`str`
        :param node_id: The UUID of the management node
        :rtype: :class:`str`
        :return: vapi service endpoint URL of a management node or, None if no vapi endpoint is found
        """
        assert node_id is not None
        result = self.__find_service_urls(product='com.vmware.cis',
                                          service='cs.vapi',
                                          endpoint='com.vmware.vapi.endpoint',
                                          protocol='vapi.json.https.public')
        assert result is not None
        return result.get(node_id)

    def find_vim_urls(self):
        """
        Finds all the vim service endpoint URLs.
        In an MxN setup where there are more than one management node; this method returns more than one URL.

        :rtype: dictionary
        :return: vim service endpoint URLs in a dictionary where the key is the node_id and the value is the service URL
        """
        return self.__find_service_urls(product='com.vmware.cis',
                                        service='vcenterserver',
                                        endpoint='com.vmware.vim',
                                        protocol='vmomi')

    def find_vim_url(self, node_id):
        """
        Finds the vim service endpoint URL of a management node

        :type: :class:`str`
        :param node_id: The UUID of the management node
        :rtype: :class:`str`
        :return: vim service endpoint URL of a management node or, None if no vim endpoint is found
        """
        assert node_id is not None
        result = self.__find_service_urls(product='com.vmware.cis',
                                          service='vcenterserver',
                                          endpoint='com.vmware.vim',
                                          protocol='vmomi')
        assert result is not None
        return result.get(node_id)

    def find_vim_pbm_urls(self):
        """
        Finds all the spbm service endpoint URLs.
        In an MxN setup where there are more than one management node; this method returns more than one URL.

        :rtype: dictionary
        :return: spbm service endpoint URLs in a dictionary where the key is the node_id and the value is the service URL
        """
        return self.__find_service_urls(product='com.vmware.vim.sms',
                                        service='sms',
                                        endpoint='com.vmware.vim.pbm',
                                        protocol='https')

    def find_vim_pbm_url(self, node_id):
        """
        Finds the spbm service endpoint URL of a management node

        :type: :class:`str`
        :param node_id: The UUID of the management node
        :rtype: :class:`str`
        :return: spbm service endpoint URL of a management node or, None if no spbm endpoint is found
        """
        assert node_id is not None
        result = self.__find_service_urls(product='com.vmware.vim.sms',
                                          service='sms',
                                          endpoint='com.vmware.vim.pbm',
                                          protocol='https')
        assert result is not None
        return result.get(node_id)

    def __find_service_urls(self, product, service, endpoint, protocol):
        """
        Finds the endpoint URLs of a service running on management nodes.
        Returns a dictionary where the key is the management node id.
        """
        assert self.client is not None
        assert self.serviceRegistration is not None

        lookupServiceRegistrationFilter = self.__create_filter_spec(product,
                                                                    service,
                                                                    endpoint,
                                                                    protocol)

        result = self.client.service.List(self.serviceRegistration,
                                          lookupServiceRegistrationFilter)
        assert len(result) > 0
        # Support for MxN
        # return the results in a dictionary where key is NodeId and Value is Service URL
        results_dict = {}
        for lookupServiceRegistrationInfo in result:
            lookupServiceRegistrationEndpoint = \
                lookupServiceRegistrationInfo.serviceEndpoints[0]
            assert lookupServiceRegistrationEndpoint is not None
            results_dict[
                lookupServiceRegistrationInfo.nodeId] = lookupServiceRegistrationEndpoint.url
        return results_dict

    def __find_platform_service_urls(self, product, service, endpoint,
                                     protocol):
        """
        Finds the endpoint URLs of a service running on PSCs (Platform Service Controller).
        Returns a list of service URLs since there is no node id associated with the PSC.
        """
        assert self.client is not None
        assert self.serviceRegistration is not None

        lookupServiceRegistrationFilter = self.__create_filter_spec(product,
                                                                    service,
                                                                    endpoint,
                                                                    protocol)

        result = self.client.service.List(self.serviceRegistration,
                                          lookupServiceRegistrationFilter)
        assert len(result) > 0

        urls = []
        for lookupServiceRegistrationInfo in result:
            lookupServiceRegistrationEndpoint = \
                lookupServiceRegistrationInfo.serviceEndpoints[0]
            assert lookupServiceRegistrationEndpoint is not None
            urls.append(lookupServiceRegistrationEndpoint.url)
        return urls

    def __create_filter_spec(self, product, service, endpoint, protocol):
        assert self.client is not None

        lookupServiceRegistrationServiceType = self.client.factory.create(
            'ns0:LookupServiceRegistrationServiceType')
        lookupServiceRegistrationServiceType.product = product
        lookupServiceRegistrationServiceType.type = service

        lookupServiceRegistrationEndpointType = self.client.factory.create(
            'ns0:LookupServiceRegistrationEndpointType')
        lookupServiceRegistrationEndpointType.type = endpoint
        lookupServiceRegistrationEndpointType.protocol = protocol

        lookupServiceRegistrationFilter = self.client.factory.create(
            'ns0:LookupServiceRegistrationFilter')
        lookupServiceRegistrationFilter.serviceType = lookupServiceRegistrationServiceType
        lookupServiceRegistrationFilter.endpointType = lookupServiceRegistrationEndpointType
        return lookupServiceRegistrationFilter

    def find_mgmt_nodes(self):
        """
        Finds all the management nodes

        :rtype: dictionary
        :return: management node instance name and node id (UUID) in a dictionary
        """
        assert self.client is not None
        assert self.serviceRegistration is not None

        lookupServiceRegistrationServiceType = self.client.factory.create(
            'ns0:LookupServiceRegistrationServiceType')
        lookupServiceRegistrationServiceType.product = 'com.vmware.cis'
        lookupServiceRegistrationServiceType.type = 'vcenterserver'

        lookupServiceRegistrationEndpointType = self.client.factory.create(
            'ns0:LookupServiceRegistrationEndpointType')
        lookupServiceRegistrationEndpointType.type = 'com.vmware.vim'
        lookupServiceRegistrationEndpointType.protocol = 'vmomi'

        lookupServiceRegistrationFilter = self.client.factory.create(
            'ns0:LookupServiceRegistrationFilter')
        lookupServiceRegistrationFilter.serviceType = lookupServiceRegistrationServiceType
        lookupServiceRegistrationFilter.endpointType = lookupServiceRegistrationEndpointType

        result = self.client.service.List(self.serviceRegistration,
                                          lookupServiceRegistrationFilter)
        assert len(result) > 0

        results_dict = {}
        for lookupServiceRegistrationInfo in result:
            for lookupServiceRegistrationAttribute in lookupServiceRegistrationInfo.serviceAttributes:
                if lookupServiceRegistrationAttribute.key == 'com.vmware.vim.vcenter.instanceName':
                    results_dict[
                        lookupServiceRegistrationAttribute.value] = lookupServiceRegistrationInfo.nodeId
        return results_dict

    def get_mgmt_node_id(self, instance_name):
        """
        Get the management node id from the instance name

        :type: :class:`str`
        :param instance_name: The instance name of the management node
        :rtype: :class:`str`
        :return: The UUID of the management node or, None is no management node is found by the given instance name
        """
        result = self.find_mgmt_nodes()
        assert result is not None
        return result.get(instance_name)

    def get_mgmt_node_instance_name(self, node_id):
        result = self.find_mgmt_nodes()
        assert result is not None
        for k, v in result.items():
            if v == node_id:
                return k

    def get_default_mgmt_node(self):
        """
        Finds the instance name and UUID of the management node for M1xN or, when the PSC and
        management services all reside on a single node (embedded).
        """
        result = self.find_mgmt_nodes()
        assert result is not None
        if len(result) < 1:
            raise Exception('No management node found')
        if len(result) > 1:
            raise MultipleManagementNodeException(
                MultipleManagementNodeException.format(result))
        return list(result.keys())[0], list(result.values())[
            0]  # python 3.x dict.keys() returns a view rather than a list


class MultipleManagementNodeException(Exception):
    def __init__(self, message):
        super(MultipleManagementNodeException, self).__init__(message)

    @staticmethod
    def format(nodes):
        """
        Formats the multiple management node exception message

        :type: :class:`dict`
        :param nodes: The dictionary containing management nodes
        :rtype: :class:`str`
        :return: Formatted string output
        """
        message = 'Multiple Management Node Found on server'
        for k, v in nodes.items():
            message = message + os.linesep + 'Node name: {0} uuid: {1}'.format(
                k, v)
        return message


def main():
    lookup_service_helper = LookupServiceHelper(
        wsdl_url='file:///path/to/lookupservice.wsdl',
        soap_url='https://server_ip/lookupservice/sdk')
    lookup_service_helper.connect()
    print(lookup_service_helper.find_sso_url())
    print(lookup_service_helper.find_vapi_urls())
    print(lookup_service_helper.find_vim_urls())
    print(lookup_service_helper.find_vim_pbm_urls())
    print(lookup_service_helper.find_mgmt_nodes())


# Start program
if __name__ == "__main__":
    main()
