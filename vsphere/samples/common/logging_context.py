"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware'
__copyright__ = 'Copyright 2013 VMware, Inc. All rights reserved.'

from os import path
import logging.config


class LoggingContext(object):
    logging.config.fileConfig(path.join(path.dirname(path.realpath(__file__)), '../../../logging.conf'), disable_existing_loggers=False)

    @classmethod
    def get_logger(cls, name):
        return logging.getLogger(name)


def main():
    logger = LoggingContext.get_logger(__name__)
    logger.critical('critical')
    logger.info('info')
    logger.debug('debug')

# Start program
# just for testing
if __name__ == "__main__":
    main()
