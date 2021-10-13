#!/usr/bin/env python

import os

from setuptools import setup

setup(name='vSphere Automation SDK',
      version='1.69.0',
      description='VMware vSphere Automation SDK for Python',
      url='https://github.com/vmware/vsphere-automation-sdk-python',
      author='VMware, Inc.',
      license='MIT',
      install_requires=[
        'lxml >= 4.3.0',
        'pyVmomi >= 6.7',
        'vapi-runtime @ file://localhost/{}/lib/vapi-runtime/vapi_runtime-2.30.0-py2.py3-none-any.whl'.format(os.getcwd()),
	  'vapi-client-bindings @ file://localhost/{}/lib/vapi-client-bindings/vapi_client_bindings-3.7.0-py2.py3-none-any.whl'.format(os.getcwd()),
	  'vapi-common-client @ file://localhost/{}/lib/vapi-common-client/vapi_common_client-2.30.0-py2.py3-none-any.whl'.format(os.getcwd()),
        'vmc-client-bindings @ file://localhost/{}/lib/vmc-client-bindings/vmc_client_bindings-1.52.0-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-python-sdk @ file://localhost/{}/lib/nsx-python-sdk/nsx_python_sdk-3.1.2.1.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-policy-python-sdk @ file://localhost/{}/lib/nsx-policy-python-sdk/nsx_policy_python_sdk-3.1.2.1.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-vmc-policy-python-sdk @ file://localhost/{}/lib/nsx-vmc-policy-python-sdk/nsx_vmc_policy_python_sdk-3.1.2.1.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'nsx-vmc-aws-integration-python-sdk @ file://localhost/{}/lib/nsx-vmc-aws-integration-python-sdk/nsx_vmc_aws_integration_python_sdk-3.1.2.1.1-py2.py3-none-any.whl'.format(os.getcwd()),
        'vmc-draas-client-bindings @ file://localhost/{}/lib/vmc-draas-client-bindings/vmc_draas_client_bindings-1.18.0-py2.py3-none-any.whl'.format(os.getcwd()),
      ]
      )
