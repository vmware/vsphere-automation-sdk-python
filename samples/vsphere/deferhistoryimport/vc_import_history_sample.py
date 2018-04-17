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
    Status, get_defer_history_import_status, get_message_as_text


class ImportHistorySample(object):
    """
    Sample demonstrating how one can change the state of the Defer History Data
    Import using its vAPI. To use this feature you need to have an appliance
    upgrade or migrated to the 6.7 or later version, using the option for
    transferring historical data after upgrade.
    """

    def __init__(self):
        self.service_manager = None

    def setup(self):
        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification
        parser = sample_cli.build_arg_parser()

        args = sample_util.process_cli_args(parser.parse_args())

        self.service_manager = ServiceManager(args.server,
                                              args.username,
                                              args.password,
                                              args.skipverification)
        self.service_manager.connect()
        atexit.register(self.service_manager.disconnect)

    def run(self):
        """
        Runs the sample's operations
        """

        try:
            # Using REST API service
            import_history = ImportHistory(self.service_manager.stub_config)

            # Change the status - either pause or resume it
            start_status = get_defer_history_import_status(import_history)
            if start_status == Status.RUNNING:
                print('Pausing Defer History Data Import.')
                import_history.pause()
                expected_status = Status.PAUSED
                revert_operation = import_history.resume
            elif start_status == Status.PAUSED:
                print('Resuming Defer History Data Import.')
                import_history.resume()
                expected_status = Status.RUNNING
                revert_operation = import_history.pause
            else:
                print('Sample can only work if the status of Defer History '
                      'Data Import is paused or running, current status '
                      'is: {0}'.format(start_status))
                return

            after_ops_status = get_defer_history_import_status(import_history)
            if after_ops_status == expected_status:
                print('Operation finished successfully.')
            else:
                print('Executed operation did not bring the process in '
                      'desired state. Current status is "{0}". '
                      'Aborting'.format(after_ops_status))
                return

            # revert to the original status
            print('Reverting to original state.')
            revert_operation()
            get_defer_history_import_status(import_history)
        except AlreadyInDesiredState:
            print('The Defer History Data Import is already in the '
                  'desired state.')
        except Error as error:
            for err in error.messages:
                print('Error: {0}'.format(get_message_as_text(err)))

    def cleanup(self):
        # Nothing to clean up
        pass


def main():
    import_history_sample = ImportHistorySample()
    import_history_sample.setup()
    import_history_sample.run()
    import_history_sample.cleanup()


if __name__ == '__main__':
    main()
