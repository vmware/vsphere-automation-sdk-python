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
from samples.vsan.snapservice.sites.probe_connection_with_vc_cert import ProbeConnectionWithCert
from samples.vsan.snapservice.tasks.task_utils import wait_for_snapservice_task

from com.vmware.snapservice_client import *


class AddSite(object):
    def __init__(self, snapservice_client, args, remote_vc_cert, va_cert):
        self._snapservice_client = snapservice_client
        self._args = args
        self._remote_vc_cert = remote_vc_cert
        self._va_cert = va_cert

    def add_task(self):
        spec = Sites.AddSpec(
            vcenter_connection_spec=Sites.VcenterConnectionSpec(host=self._args.remote_vc_host, port=443),
            vcenter_creds=Sites.UserCredentials(user=self._args.remote_vc_user, password=self._args.remote_vc_password),
            vcenter_certificate=self._remote_vc_cert,
            va_certificate=self._va_cert)
        return self._snapservice_client.Sites.add_task(spec)


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

    probe_conn_with_cert = AddSite(clients.snapservice_client, args,
                                   resp.vcenter_certificate.certificate, with_cert_resp.va_certificate.certificate)
    add_task = probe_conn_with_cert.add_task()

    print('Add site task:')
    print('----------------------------------------')
    print(add_task.task_id)
    print('----------------------------------------')

    wait_for_snapservice_task(clients.snapservice_client, add_task.task_id)


if __name__ == '__main__':
    main()
