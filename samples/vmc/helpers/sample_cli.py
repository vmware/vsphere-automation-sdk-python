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
Builds a standard argument parser with required and optional argument groups

Most of the VMC samples require these three standard required arguments.
If any of these arguments are not required, then build your own parser

--refresh_token
--org_id
--sddc_id

"""
parser = argparse.ArgumentParser()

required_args = parser.add_argument_group(
        'required arguments')
optional_args = parser.add_argument_group(
        'optional arguments')

required_args.add_argument(
        '--refresh_token',
        required=True,
        help='Refresh token obtained from CSP')
required_args.add_argument(
        '--org_id',
        required=True,
        help='Orgization ID')
required_args.add_argument(
        '--sddc_id',
        required=True,
        help='SDDC ID')
