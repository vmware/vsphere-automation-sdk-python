#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2024 Broadcom. All Rights Reserved.
* Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
* and/or its subsidiaries.
* SPDX-License-Identifier: MIT
* *******************************************************
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0+'

from pprint import pprint

from com.vmware.vcenter.trusted_infrastructure.hosts.hardware_client import Tpm
from com.vmware.vcenter.trusted_infrastructure.hosts.hardware.tpm_client import EndorsementKeys
from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common import vapiconnect
from samples.vsphere.common.ssl_helper import get_unverified_session


class TPMInfo(object):
    """
    Demonstrates how to get TPM Information for the Host
    attached to vCenter.

    Sample Prerequisites:
    vCenter/ESX(TPM enabled)
    """
    def __init__(self):
        self.stub_config = None
        self.hostId = None

        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None

        # Login to vSphere client to get attached Host information.
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)
        for host in self.client.vcenter.Host.list():
            self.hostId = host.host

        # Connect to the trusted infrastructure services.
        self.stub_config = vapiconnect.connect(host=args.server,
                                               user=args.username,
                                               pwd=args.password,
                                               skip_verification=args.skipverification)
        self.tpm_svc = Tpm(self.stub_config)
        self.ek_svc = EndorsementKeys(self.stub_config)

    def run(self):
        tpmList = self.tpm_svc.list(self.hostId)
        for tpm in tpmList:
            tpmId = tpm.tpm
            tpmInfo = self.tpm_svc.get(self.hostId, tpmId)
            print("----------------------------")
            print("TPM Information")
            print("----------------------------")
            pprint("major_version: %s" % tpmInfo.major_version)
            pprint("minor_version: %s" % tpmInfo.minor_version)
            pprint("active: %s" % tpmInfo.active)
            if tpmInfo.manufacturer:
                pprint("manufacturer: %s" % tpmInfo.manufacturer)
            if tpmInfo.model:
                pprint("model: %s" % tpmInfo.model)
            if tpmInfo.firmware_version:
                pprint("firmware_version: %s" % tpmInfo.firmware_version)
            print("----------------------------")

        eksList = self.ek_svc.list(self.hostId, tpmId)
        for ek in eksList:
            keyId = ek.key
            ekInfo = self.ek_svc.get(self.hostId, tpmId, keyId)
            if ekInfo.public_key:
                print("----------------------------")
                print("TPM Endorsement key")
                print("----------------------------")
                pprint(ekInfo.public_key)
                print("----------------------------")


def main():
    tpm_info = TPMInfo()
    tpm_info.run()


if __name__ == '__main__':
    main()
