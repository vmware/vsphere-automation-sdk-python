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
__vcenter_version__ = '7.0+'

from samples.vsphere.common.sample_cli import build_arg_parser

"""
Builds a standard argument parser with required and optional argument groups
Most of the Vsphere Stats samples require these three standard required
arguments.
--expiration
--interval
"""
parser = build_arg_parser()

required_args = parser.add_argument_group(
        'required arguments for creating acquisition spec')

required_args.add_argument(
        '--expiration',
        required=True,
        help='Create an Acquisition Specification with expiration time.' +
        ' Example: 10000000000')

required_args.add_argument(
        '--interval',
        required=True,
        help='Create an Acquisition Specification with interval. Example: 10')
