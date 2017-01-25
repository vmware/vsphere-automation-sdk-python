"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

"""
This module implements simple helper functions for python samples
"""
import argparse


def build_arg_parser():
    """
    Builds a standard argument parser with arguments for executing sample
    setup script

    -s, --testbed_setup
    -t, --testbed_validate
    -c, --testbed_cleanup
    -o, --iso_cleanup
    -e, --samples_setup
    -r, --samples
    -i, --samples_incremental
    -l, --samples_cleanup
    -v, --skipverification

    """
    parser = argparse.ArgumentParser(
        description='Arguments for running sample setup script')

    parser.add_argument('-s', '--testbed_setup',
                        action='store_true',
                        help='Build the testbed.  Will run cleanup before '
                             'trying to build in case there is '
                             'an intermediate failure')

    parser.add_argument('-t', '--testbed_validate',
                        action='store_true',
                        help='Validate if the testbed is ready for the samples')

    parser.add_argument('-c', '--testbed_cleanup',
                        action='store_true',
                        help='Tear down the testbed')

    parser.add_argument('-o', '--iso_cleanup',
                        action='store_true',
                        help='Delete iso during cleanup. ')

    parser.add_argument('-e', '--samples_setup',
                        action='store_true',
                        help='Run sample setup. ')

    parser.add_argument('-r', '--samples',
                        action='store_true',
                        help='Run samples. ')

    parser.add_argument('-i', '--samples_incremental',
                        action='store_true',
                        help='Runs samples that incrementally updates the VM '
                             'configuration. ')

    parser.add_argument('-l', '--samples_cleanup',
                        action='store_true',
                        help='Clean up after sample run. ')

    parser.add_argument('-v', '--skipverification',
                        action='store_true',
                        help='Verify server certificate when connecting to '
                             'vcenter. ')

    return parser
