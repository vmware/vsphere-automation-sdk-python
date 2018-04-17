#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
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
__copyright__ = 'Copyright 2017 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.7+'

import atexit

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.service_manager import ServiceManager

from com.vmware.vcenter.deployment_client import ImportHistory
from com.vmware.vapi.std.errors_client import NotAllowedInCurrentState, \
    Error, Unauthenticated, AlreadyInDesiredState, Unauthorized

from samples.vsphere.deferhistoryimport.vc_import_history_common import \
    get_defer_history_import_status, get_message_as_text


class ImportHistorySampleCli(object):
    """
    Sample demonstrating how the API for the upgrade's Defer History Data
    Import feature can be used. To use this feature you need to have an
    appliance upgrade or migrated to the 6.7 or later version, using the
    option for transferring historical data after upgrade.
    """
    def __init__(self):
        self.service_manager = None
        self.operation = None

    def setup(self):
        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification
        parser = sample_cli.build_arg_parser()

        parser.add_argument('-o', '--operation',
                            action='store',
                            default='status',
                            choices=['status',
                                     'start',
                                     'pause',
                                     'resume',
                                     'cancel'],
                            help='Operation to execute')

        args = sample_util.process_cli_args(parser.parse_args())
        self.operation = args.operation

        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

    def run(self):
        """
        Runs the requested operation
        """

        # Using REST API service
        import_history = ImportHistory(self.service_manager.stub_config)

        if self.operation == 'status':
            get_defer_history_import_status(import_history)
            return

        try:
            operations = {
                'start': import_history.start,
                'pause': import_history.pause,
                'resume': import_history.resume,
                'cancel': import_history.cancel
            }
            print('Executing operation "{0}"'.format(self.operation))
            if self.operation in operations:
                operations[self.operation]()
                print('Executing operation "{0}" was successful'.format(
                      self.operation))
            else:
                print('Unknown operation {0}'.format(self.operation))
        except AlreadyInDesiredState:
            print('The Defer History Data Import is already in the '
                  'desired state.')
        except Error as error:
            print('Request "{0}" returned error.'.format(self.operation))
            for err in error.messages:
                print('Error: {0}'.format(get_message_as_text(err)))

    def cleanup(self):
        # Nothing to clean up
        pass


def main():
    import_history_sample_cli = ImportHistorySampleCli()
    import_history_sample_cli.setup()
    import_history_sample_cli.run()
    import_history_sample_cli.cleanup()


if __name__ == '__main__':
    main()
