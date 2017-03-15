"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013, 2016. All Rights Reserved.
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
__copyright__ = 'Copyright 2013, 2016 VMware, Inc. All rights reserved.'

from samples.vsphere.common.service_manager import ServiceManager


class ServiceManagerFactory(object):
    """
    Factory class for getting service manager for a management node.
    """
    service_manager = None

    @classmethod
    def get_service_manager(cls, server, username, password, skip_verification):
        cls.service_manager = ServiceManager(server,
                                             username,
                                             password,
                                             skip_verification)
        cls.service_manager.connect()
        return cls.service_manager

    @classmethod
    def disconnect(cls):
        if cls.service_manager:
            cls.service_manager.disconnect()


import atexit
atexit.register(ServiceManagerFactory.disconnect)
