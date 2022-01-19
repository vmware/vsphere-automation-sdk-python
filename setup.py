#!/usr/bin/env python

import os
from pip.req import parse_requirements
from setuptools import setup

install_reqs = parse_requirements(<requirements_path>)
reqs = [str(ir.req) for ir in install_reqs]

setup(name='vSphere Automation SDK',
      version='1.71.0',
      description='VMware vSphere Automation SDK for Python',
      url='https://github.com/vmware/vsphere-automation-sdk-python',
      author='VMware, Inc.',
      license='MIT',
      install_requires=reqs
)
