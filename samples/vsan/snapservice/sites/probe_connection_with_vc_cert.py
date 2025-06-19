#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '8.0.3+'

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsan.snapservice.data_protection_clients import DataProtectionClients
from samples.vsan.snapservice.sites.probe_connection import ProbeConnection

from com.vmware.snapservice_client import *


class ProbeConnectionWithCert(object):
    def __init__(self, snapservice_client, args, remote_vc_cert):
        self._snapservice_client = snapservice_client
        self._args = args
        self._remote_vc_cert = remote_vc_cert

    def probe(self):
        spec = Sites.ProbeSpec(
            vcenter_connection_spec=Sites.VcenterConnectionSpec(host=self._args.remote_vc_host, port=443),
            vcenter_creds=Sites.UserCredentials(user=self._args.remote_vc_user, password=self._args.remote_vc_password),
            vcenter_certificate=self._remote_vc_cert
        )
        return self._snapservice_client.Sites.probe(spec)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--remote_vc_host',
                               action='store',
                               required=True,
                               help='Remote VC hostname for site pairing')
    required_args.add_argument('--remote_vc_user',
                               action='store',
                               required=True,
                               help='Remote VC username for site pairing')
    required_args.add_argument('--remote_vc_password',
                               action='store',
                               required=True,
                               help='Remote VC password for site pairing')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    probe_conn = ProbeConnection(clients.snapservice_client, args)
    resp = probe_conn.probe()

    probe_conn_with_cert = ProbeConnectionWithCert(clients.snapservice_client, args,
                                                   resp.vcenter_certificate.certificate)
    with_cert_resp = probe_conn_with_cert.probe()

    print('Probe with vc cert response:')
    print('----------------------------------------')
    print(with_cert_resp)
    print('----------------------------------------')


if __name__ == '__main__':
    main()
