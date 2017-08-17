#!/usr/bin/env python

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


"""
Script that runs through all the setup and samples.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'


import pyVim.connect
from samples.vsphere.common import sample_util
from samples.vsphere.common import vapiconnect
from samples.vsphere.vcenter.setup import testbed
from samples.vsphere.vcenter.setup.setup_cli import build_arg_parser
from samples.vsphere.vcenter.setup.testbed_setup import cleanup as testbed_cleanup
from samples.vsphere.vcenter.setup.testbed_setup import setup as testbed_setup
from samples.vsphere.vcenter.setup.testbed_setup import validate as testbed_validate
from samples.vsphere.vcenter.vm.main import cleanup as sample_cleanup
from samples.vsphere.vcenter.vm.main import run as sample_run

from samples.vsphere.common.ssl_helper import get_unverified_context


# Parse command line params for setup script
args = build_arg_parser().parse_args()

_testbed = testbed.get()

# If VC/ESX/NFS Server IPs are passed as arguments,
# then override testbed.py values
if (args.vcenterserver):
    _testbed.config['SERVER'] = args.vcenterserver
if (args.vcenterpassword):
    _testbed.config['PASSWORD'] = args.vcenterpassword
if (args.esxhost1):
    _testbed.config['ESX_HOST1'] = args.esxhost1
if (args.esxhost2):
    _testbed.config['ESX_HOST2'] = args.esxhost2
if (args.esxpassword):
    _testbed.config['ESX_PASS'] = args.esxpassword
if (args.nfsserver):
    _testbed.config['NFS_HOST'] = args.nfsserver


print(_testbed.to_config_string())

# Connect to VIM API Endpoint on vCenter system
context = None
if args.skipverification:
    context = get_unverified_context()
service_instance = pyVim.connect.SmartConnect(host=_testbed.config['SERVER'],
                                              user=_testbed.config['USERNAME'],
                                              pwd=_testbed.config['PASSWORD'],
                                              sslContext=context)

# Connect to vAPI Endpoint on vCenter system
stub_config = vapiconnect.connect(host=_testbed.config['SERVER'],
                                  user=_testbed.config['USERNAME'],
                                  pwd=_testbed.config['PASSWORD'],
                                  skip_verification=args.skipverification)

context = sample_util.Context(_testbed, service_instance, stub_config)

context.option['DO_TESTBED_SETUP'] = args.testbed_setup
context.option['DO_TESTBED_VALIDATE'] = args.testbed_validate
context.option['DO_TESTBED_CLEANUP'] = args.testbed_cleanup
context.option['DO_TESTBED_ISO_CLEANUP'] = args.iso_cleanup
context.option['DO_SAMPLES_SETUP'] = args.samples_setup
context.option['DO_SAMPLES'] = args.samples
context.option['DO_SAMPLES_INCREMENTAL'] = args.samples_incremental
context.option['DO_SAMPLES_CLEANUP'] = args.samples_cleanup
context.option['SKIP_VERIFICATION'] = args.skipverification
print(context.to_option_string())

###############################################################################
# Testbed Setup
###############################################################################

# Setup testbed
if context.option['DO_TESTBED_SETUP']:
    # Clean up in case of past failures
    sample_cleanup(context)
    testbed_cleanup(context)
    testbed_setup(context)

# Validate testbed
if (context.option['DO_TESTBED_SETUP'] or
        context.option['DO_TESTBED_VALIDATE'] or
        context.option['DO_SAMPLES_SETUP'] or
        context.option['DO_SAMPLES']):
    if not testbed_validate(context):
        exit(0)
    print(context.testbed.to_entities_string())

###############################################################################
# Sample Run and Cleanup
###############################################################################

# Run Sample
if context.option['DO_SAMPLES']:
    sample_run(context)

# Cleanup after sample run
if context.option['DO_SAMPLES_CLEANUP']:
    sample_cleanup(context)

###############################################################################
# Testbed Cleanup
###############################################################################

# Teardown testbed.
if context.option['DO_TESTBED_CLEANUP']:
    sample_cleanup(context)
    testbed_cleanup(context)
