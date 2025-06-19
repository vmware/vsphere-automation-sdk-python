"""
* *******************************************************
* Copyright (c) 2025 Broadcom. All Rights Reserved.
* Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
* and/or its subsidiaries.
* SPDX-License-Identifier: MIT
* *******************************************************
"""

__author__ = 'Broadcom, Inc.'
__copyright__ = 'Copyright 2025 Broadcom, Inc. All rights reserved.'


# Required to distribute different parts of this
# package as multiple distribution
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)  # @ReservedAssignment
