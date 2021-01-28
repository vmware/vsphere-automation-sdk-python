#!/usr/bin/env python

import os

from setuptools import setup

setup(name='vSphere Automation SDK',
      version='1.46.0',
      description='VMware vSphere Automation SDK for Python',
      url='https://github.com/vmware/vsphere-automation-sdk-python',
      author='VMware, Inc.',
      license='MIT',
      install_requires=[
        'lxml >= 4.3.0',
        'suds ; python_version < "3"',
        'suds-jurko ; python_version >= "3.0"',
        'pyVmomi >= 6.7',
        'vapi-runtime==2.19.0',
        'vapi-client-bindings==3.5.0',
        'vapi-common-client==2.19.0',
        'vmc-client-bindings==1.32.0',
        'nsx-python-sdk==3.0.2.0.0.16837625',
        'nsx-policy-python-sdk==3.0.2.0.0.16837625',
        'nsx-vmc-policy-python-sdk==3.0.2.0.0.16837625',
        'nsx-vmc-aws-integration-python-sdk==3.0.2.0.0.16837625',
        'vmc-draas-client-bindings==1.17.0',
      ],
      dependency_links=[
        'https://cdn.githubraw.com/vmware/vsphere-automation-sdk-python/master/lib/',
      ])
