"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'

import argparse


def build_arg_parser():
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -s server
    -u username
    -p password
    -c cleanup
    -v skipverification

    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    parser.add_argument('-s', '--server',
                        action='store',
                        help='vSphere service IP to connect to')

    parser.add_argument('-u', '--username',
                        action='store',
                        help='Username to use when connecting to vc')

    parser.add_argument('-p', '--password',
                        action='store',
                        help='Password to use when connecting to vc')

    parser.add_argument('-c', '--cleardata',
                        action='store_true',
                        help='Clean up after sample run. ')

    parser.add_argument('-v', '--skipverification',
                        action='store_true',
                        help='Verify server certificate when connecting to vc.')

    return parser
