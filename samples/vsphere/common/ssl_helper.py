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
__copyright__ = 'Copyright 2016 VMware, Inc. All rights reserved.'

import ssl


def get_unverified_context():
    """
    Get an unverified ssl context. Used to disable the server certificate
    verification.
    @return: unverified ssl context.
    """
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    return context
