#!/usr/bin/env python

from setuptools import setup

setup(name='vSphere Automation SDK',
      version='1.0.0',
      description='VMware vSphere Automation SDK for Python',
      url='https://github.com/vmware/vsphere-automation-sdk-python',
      author='VMware, Inc.',
      license='MIT',
      install_requires=[
        'lxml >= 4.3.0',
        'suds ; python_version < "3"',
        'suds-jurko ; python_version >= "3.0"',
        'pyVmomi >= 6.7',
        'vapi-runtime @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/vapi-runtime/vapi_runtime-2.12.0-py2.py3-none-any.whl',
        'vapi-client-bindings @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/vapi-client-bindings/vapi_client_bindings-3.0.0-py2.py3-none-any.whl',
        'vapi-common-client @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/vapi-common-client/vapi_common_client-2.12.0-py2.py3-none-any.whl',
        'vmc-client-bindings @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/vmc-client-bindings/vmc_client_bindings-1.6.0-py2.py3-none-any.whl',
        'nsx-python-sdk @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/nsx-python-sdk/nsx_python_sdk-2.3.0.0.3.13851140-py2.py3-none-any.whl',
        'nsx-policy-python-sdk @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/nsx-policy-python-sdk/nsx_policy_python_sdk-2.3.0.0.3.13851140-py2.py3-none-any.whl',
        'nsx-vmc-policy-python-sdk @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/nsx-vmc-policy-python-sdk/nsx_vmc_policy_python_sdk-2.3.0.0.3.13851140-py2.py3-none-any.whl',
        'nsx-vmc-aws-integration-python-sdk @ https://github.com/vmware/vsphere-automation-sdk-python/raw/master/lib/nsx-vmc-aws-integration-python-sdk/nsx_vmc_aws_integration_python_sdk-2.3.0.0.3.13851140-py2.py3-none-any.whl'
      ]
      )
