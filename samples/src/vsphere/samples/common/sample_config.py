"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013, 2016. All Rights Reserved.
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2013, 2016 VMware, Inc. All rights reserved.'

from os import path
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class SampleConfig(object):
    config = configparser.RawConfigParser()
    config.read(path.join(path.dirname(path.realpath(__file__)), '../../../sample.cfg'))

    @classmethod
    def get_sample_config(cls):
        return cls.config

    @classmethod
    def get_server_url(cls):
        config = SampleConfig.get_sample_config()
        return config.get('connection', 'server')

    @classmethod
    def get_username(cls):
        config = SampleConfig.get_sample_config()
        return config.get('connection', 'username')

    @classmethod
    def get_password(cls):
        config = SampleConfig.get_sample_config()
        return config.get('connection', 'password')


def main():
    print('serverurl: {0}'.format(SampleConfig.get_server_url()))
    print('username: {0}'.format(SampleConfig.get_username()))
    print('password: {0}'.format(SampleConfig.get_password()))

# Start program
# just for testing
if __name__ == "__main__":
    main()
