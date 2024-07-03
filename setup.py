#!/usr/bin/env python

import os

from setuptools import setup

setup(name='vsphere-automation-sdk',
      version='1.87.0',
      description='VMware vSphere Automation SDK for Python',
      url='https://github.com/vmware/vsphere-automation-sdk-python',
      author='Broadcom, Inc.',
      license='MIT',
      packages=[],
      install_requires=[
        'lxml >= 4.3.0',
        'pyVmomi == 8.0.3.0.1',
        'vmware-vapi-runtime == 2.52.0',
        'vmware-vcenter == 8.0.3.0',
        'vmware-vapi-common-client == 2.52.0',
        'vmwarecloud-aws @ file://localhost/{}/lib/vmwarecloud-aws/vmwarecloud_aws-1.64.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-python-sdk @ file://localhost/{}/lib/nsx-python-sdk/nsx_python_sdk-4.2.0-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-policy-python-sdk @ file://localhost/{}/lib/nsx-policy-python-sdk/nsx_policy_python_sdk-4.2.0-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-vmc-policy-python-sdk @ file://localhost/{}/lib/nsx-vmc-policy-python-sdk/nsx_vmc_policy_python_sdk-4.1.2.0.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-vmc-aws-integration-python-sdk @ file://localhost/{}/lib/nsx-vmc-aws-integration-python-sdk/nsx_vmc_aws_integration_python_sdk-4.1.2.0.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'vmwarecloud-draas @ file://localhost/{}/lib/vmwarecloud-draas/vmwarecloud_draas-1.23.1-py2.py3-none-any.whl'.format(os.getcwd()),
      ]
)
