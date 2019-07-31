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
__copyright__ = 'Copyright 2019 VMware, Inc. All rights reserved.'

import argparse

"""
Builds a standard argument parser with required and optional argument
groups

--refresh_token

"""
parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

required_args = parser.add_argument_group(
        'required arguments')
optional_args = parser.add_argument_group(
        'optional arguments')
    
required_args.add_argument(
        '--refresh_token',
        required=True,
        help='Refresh token obtained from CSP')
