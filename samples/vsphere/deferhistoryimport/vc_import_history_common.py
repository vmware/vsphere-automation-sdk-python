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


class Status(object):
    """ Constant used to indicate what is the current status
    """
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    CANCELED = 'Canceled'
    PAUSED = 'Paused'
    NOT_STARTED = 'Not started'
    UNKNOWN = 'Unknown'

    @staticmethod
    def parse(apiStatus):
        """ Parses an API status and returns Status constant based on it
        """
        return STATUS_TRANSLATION_MATRIX.get(apiStatus, Status.UNKNOWN)


STATUS_TRANSLATION_MATRIX = {
    'RUNNING': Status.RUNNING,
    'SUCCEEDED': Status.SUCCEEDED,
    'FAILED': Status.CANCELED,
    'BLOCKED': Status.PAUSED,
    'PENDING': Status.NOT_STARTED
}


def get_message_as_text(msg):
        """
        Creates displayable message in correct form from a message of
        the API. There will be no translations.

        @param msg: Message returned by the API
        @type msg: LocalizableMessage
        """
        if not msg:
            return None
        return msg.default_message % msg.args


def get_defer_history_import_status(import_history):
        """
        Gets the status of the Defer History Data Import and print it to
        the stdout. It does not do exception handling.

        Stdout example output for running status:

        --------------------
        Defer History Data Import Status: Running
        Description: vCenter Server history import
        Started: 2017-10-24 14:30:50.752000
        Progress: 10%
        Last progress message: Importing historical data...
        --------------------

        @param import_history: object representing the vAPI Endpoint
        @type import_history: deployment_client.ImportHistory

        @return: status of the Defer History Data Import
        @rtype: Status
        """
        result = import_history.get()

        if not result:
            print('Could not acquire status of Defer History Data Import. '
                  'Aborting.')
            return Status.UNKNOWN

        delimitar = '-' * 20
        print(delimitar)

        status = Status.parse(result.status)
        print('Defer History Data Import Status: {0}'.format(status))
        description = get_message_as_text(result.description)
        print('Description: {0}'.format(description))
        if result.start_time:
            print('Started: {0}'.format(result.start_time))

        if result.end_time:
            print('Finished: {0}'.format(result.end_time))

        # Progress is reported as completed steps out of total and
        # need to be calculated at the clients side if want to be reported
        # as percentages
        progress = result.progress
        if progress:
            print('Progress: {0}%'.format(progress.completed))
            progress_message = get_message_as_text(progress.message)
            print('Last progress message: {0}'.format(progress_message))

        if result.error:
            print('Error: {0}'.format(get_message_as_text(result.error)))

        for msg in result.result.errors:
            print('Error: {0}'.format(get_message_as_text(msg)))

        for msg in result.result.warnings:
            print('Warning: {0}'.format(get_message_as_text(msg)))

        for msg in result.result.info:
            print('Message: {0}'.format(get_message_as_text(msg)))

        print(delimitar)
        return status
