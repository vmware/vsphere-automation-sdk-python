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
__copyright__ = 'Copyright 2020 VMware, Inc. All rights reserved.'
__vcenter_version__ = '7.0+'

from pprint import pprint
import os

from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session


class CustomizationSpecManager(object):
    """
    Demonstrates import/export customizationSpecs in vCenter
    Sample Prerequisites: 1 vcenter, no ESXi nor VM needed
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)
        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs
        filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'sample_import.json')
        with open(filePath, 'r') as f:
            self.jsonDataRaw = f.read()
        self.specName = 'defaultCustSpec01'
        self.specsAdded = []

    def listCustomizationSpecs(self):
        """
        List CustomizationSpecs present in vc server
        """
        print("------------list--------------")
        print("List Of  CustomizationSpecs:")
        list_of_specs = self.specs_svc.list()
        pprint(list_of_specs)

    def importSpecTest(self):
        print("--------import and create Customizationpec from json--------")
        # CreateSpec
        create_spec = self.specs_svc.import_specification(self.jsonDataRaw)
        # svc Create
        self.specs_svc.create(spec=create_spec)
        # append it to existing list, for delete and cleanup
        self.specsAdded.append(self.specName)
        # list after create
        self.listCustomizationSpecs()
        print("----------------------------")

    def exportSpecTest(self):
        print("-----------Get existing Spec------------")
        # Get a spec, modify its timezone and description
        mySpecXml = self.specs_svc.export(self.specName, 'XML')
        pprint(mySpecXml)
        mySpecJson = self.specs_svc.export(self.specName, 'JSON')
        pprint(mySpecJson)
        print("----------------------------")

    def deleteSpecTest(self):
        print("-----------Delete created spec for cleanup------------")
        print("-----------before delete------------")
        self.listCustomizationSpecs()
        for specName in self.specsAdded:
            self.specs_svc.delete(specName)
        # list again, there should be []
        print("-----------after delete------------")
        self.listCustomizationSpecs()
        print("----------------------------")


def main():
    myCustSpecMgr = CustomizationSpecManager()
    myCustSpecMgr.listCustomizationSpecs()
    myCustSpecMgr.importSpecTest()
    myCustSpecMgr.exportSpecTest()
    myCustSpecMgr.deleteSpecTest()


if __name__ == '__main__':
    main()
