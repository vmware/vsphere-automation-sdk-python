"""
* *******************************************************
* Copyright (c) VMware, Inc. 2013. All Rights Reserved.
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
__copyright__ = 'Copyright 2013 VMware, Inc. All rights reserved.'


import uuid
import string
import random


def generate_random_uuid():
    return str(uuid.uuid4())


def rand(value):
    return value + generate_random_string(5)


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase) for _i in range(length))


def main():
    print(generate_random_uuid())
    print(generate_random_string(5))
    print(rand('Simple VM-'))


# Start program
if __name__ == "__main__":
    main()
