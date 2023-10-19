# VMware vSphere Automation SDK for Python  
[![Build Status](https://travis-ci.com/vmware/vsphere-automation-sdk-python.svg?token=v9mEJjcpDiQ9DrYbzyaQ&branch=master)](https://travis-ci.com/vmware/vsphere-automation-sdk-python)

## Table of Contents
- [Abstract](#abstract)
- [Supported vCenter Releases](#supported-vcenter-releases)
- [Supported NSX-T Releases](#supported-nsx-t-releases)
- [VMware Cloud on AWS Support](#vmware-cloud-on-aws-support)
- [Quick Start Guide](#quick-start-guide)
- [Run SDK Samples](#run-sdk-samples)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Support](#support)
- [Repository Administrator Resources](#repository-administrator-resources)
- [VMware Resources](#vmware-resources)

## Abstract
This document describes the vSphere Automation Python SDK samples that use the vSphere Automation
python client library. Additionally, some of the samples demonstrate the combined use of the
vSphere Automation and vSphere APIs. To support this combined use, the vSphere Automation Python SDK
samples require the vSphere Management SDK packages (pyVmomi) to be installed on the client.
The samples have been developed to work with python 3.8+

## Supported OnPrem vCenter Releases
vCenter 7.0, 7.0U1, 7.0U2, 7.0U3 , 8.0, 8.0U1, 8.0U2
Please refer to the notes in each sample for detailed compatibility information.

## Supported NSX-T Releases
NSX-T 2.2 - 4.1.2 and VMC 1.7 - 1.24

## Latest VMware Cloud on AWS Release:
VMC M24 (1.24) ([Release Notes](https://docs.vmware.com/en/VMware-Cloud-on-AWS/0/rn/vmc-on-aws-relnotes.html))

## Quick Start Guide

### Prepare a Python Development Environment

We recommend you to install latest [Python](http://docs.python-guide.org/en/latest/starting/installation/) and [pip](https://pypi.python.org/pypi/pip/) on your system.

A Python virtual environment is also highly recommended.
* [Install a virtual env for Python 3](https://docs.python.org/3/tutorial/venv.html)

### Installing Required Python Packages
SDK package installation commands may differ depending on the environment where it is being installed. The three installation options provided below are for different environments.
*pip* and *setuptools* are common requirements for these installation types, upgrade to the latest *pip* and *setuptools*.

**NOTE:** The SDK also requires OpenSSL 1.0.1+ in order to support TLS1.1 & 1.2

##### 1. Typical Installation
This is the recommended way to install the SDK. The installation is done from [PyPI](https://pypi.org/) and [Automation SDK Python Github](https://github.com/vmware/vsphere-automation-sdk-python) repositories.

Install/Update latest pip from PyPI.
```cmd
pip install --upgrade pip
```
Install/Update setuptools
```cmd
pip install --upgrade setuptools
```
Install SDK packages from Github.
```cmd
pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
```

##### 2. Local installation
Local installation can be used in an environment which either do not have Github access or users do not want to install from Github repository.

Install all the wheel files from SDK's lib directory.
```cmd
pip install -U lib/*/*.whl
```
Install dependencies like *lxml* and *pyvmomi* from PyPI as other requirements were installed from SDK's lib directory.
```cmd
pip install -U <SDK_DIRECTORY_PATH>
```
Where <SDK_DIRECTORY_PATH> is either install directory of the SDK or location of SDK's zip
e.g.
```
pip install -U /root/vsphere-automation-sdk-python
Or
pip install -U vsphere-automation-sdk-python-8.0.0.0.zip
```
##### 3. Installation in an air gap environment
For this type of environment an additional step is required to ensure SDK's dependencies are available.
Following dependencies have to be downloaded from PyPI and transferred to the air gap environment.

**NOTE:** This step has to be done in an environment which has PyPI access.
```cmd
pip download  -r requirements_pypi.txt -d lib
zip -r lib.zip lib/
```
Follow these steps in the air gap environment.
Unzip the lib.zip under automation SDK home directory.
```cmd
unzip lib.zip
```
Install all the dependencies and packages.
```cmd
pip install -U lib/**/*.whl
```
This is to install the "vSphere-Automation-SDK" which provides an SDK version. It also ensures that all the SDK requirements are installed. If not, the installation will fail.
```cmd
pip install -U `pwd`
```

### Connect to a vCenter Server

```python
import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client
session = requests.session()

# Disable cert verification for demo purpose. 
# This is not recommended in a production environment.
session.verify = False

# Disable the secure connection warning for demo purpose.
# This is not recommended in a production environment.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to a vCenter Server using username and password
vsphere_client = create_vsphere_client(server='<vc_ip>', username='<vc_username>', password='<vc_password>', session=session)

# List all VMs inside the vCenter Server
vsphere_client.vcenter.VM.list()
```

Output in a Python Interpreter:

```shell
(venv) het-m03:vsphere-automation-sdk-python het$ python
Python 3.9.8 (main, Nov 10 2021, 06:03:50)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> import urllib3
>>> from vmware.vapi.vsphere.client import create_vsphere_client
>>> session = requests.session()
>>> session.verify = False
>>> urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
>>> vsphere_client = create_vsphere_client(server='<vc_ip>', username='<vc_username>', password='<vc_password>', session=session)
>>> vsphere_client.vcenter.VM.list()
[Summary(vm='vm-58', name='standalone-20e4bd3af-esx.0-vm.0', power_state=State(string='POWERED_OFF'), cpu_count=1, memory_size_mib=256), 
...]
```

**NOTE:** If you are using Bash, be sure to use single quote for username and password to preserve the values. If you use double quote, you will have to escape special characters, such as "$". See [Bash manual](http://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html) 

### Connect to VMware Cloud on AWS

```python
from vmware.vapi.vmc.client import create_vmc_client

# Connect to VMware Cloud on AWS using refresh token
vmc_client = create_vmc_client('<refresh_token>')

# Get organizations associated with calling user.
vmc_client.Orgs.list()
```

Output in a Python Interpreter:

```shell
(venv) het-m03:vsphere-automation-sdk-python het$ python
Python 3.9.8 (main, Nov 10 2021, 06:03:50)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from vmware.vapi.vmc.client import create_vmc_client
>>> vmc_client = create_vmc_client('<refresh_token>')
>>> vmc_client.Orgs.list()
[Organization(updated=datetime.datetime(2018, 3, 2, 16, 57, 46), user_id='77aa6e6f-3257-3637-9cd9-14fae3a25b9d', updated_by_user_id='2021b5ae-890b-3472-ba9a-bc8cff776ca7', created=datetime.datetime(2017, 4, 4, 11, 57, 48, 861), version=15, updated_by_user_name='mdreyer@vmware.com', user_name='pgifford@vmware.com', id='2a8ac0ba-c93d-4748-879f-7dc9918beaa5', display_name='VMC-SET', name='j13hqg73', sla='VMC_INTERNAL', project_state='CREATED', properties=OrgProperties(values={'defaultAwsRegions': 'US_WEST_2,US_EAST_1', 'sddcLimit': '5', 'planVersion': '3.0', 'defaultHostsPerSddc': '4', 'invitationCode': '/csp/gateway/slc/api/service-invitations/aa7203c3617bbe755597b8b0ad652', 'enableAWSCloudProvider': 'true', 'enableZeroCloudCloudProvider': 'true', 'accountLinkingOptional': 'false', 'defaultPDXDatacenter': 'pdx2', 'skipSubscriptionCheck': 'true', 'minHostsPerSddc': '4', 'maxHostsPerSddc': '8', 'hostLimit': '16', 'maxHostsPerSddcOnCreate': '4', 'isAllAccess': 'true', 'enabledAvailabilityZones': '{"us-east-1":["iad6","iad7","iad12"],"us-west-2":["pdx1", "pdx4", "pdx2"]}'}), cloud_configurations={'AWS': AwsOrgConfiguration(provider='AWS')})
...]
```

## Run SDK Samples

In this section we will walk you through the steps to run the sample code for vSphere 
and VMware Cloud on AWS APIs. 

### First, set PYTHONPATH to use SDK helper methods  

* Linux/Mac:

    export PYTHONPATH=${PWD}:$PYTHONPATH

* Windows:

    set PYTHONPATH=%cd%;%PYTHONPATH%

### Run VMware Cloud on AWS Samples

```cmd
$ python samples/vmc/orgs/organization_operations.py -r <refresh_token>
```

### Run vSphere Samples

A vSphere test environment is required with the following configuration:
* 1 vCenter Server
* 2 ESX hosts
* 1 NFS Datastore with at least 3GB of free capacity

**Note** Please have the details of these available but do not have any configuration pre-created on vCenter server or ESXi Hosts, for example there should be no existing datacenters, clusters or attached hosts on the vCenter server.

#### Running the SDK Sample Setup Script

Before executing the samples we'll need to setup the vSphere test environment using one of the sample scripts (samples/vsphere/vcenter/setup/main.py). The script will perform the following:

* Create 2 test Datacenters 
* Create a test Cluster
* Create Test Folders for VM Storage
* Attach the hosts
* Create a Distributed Switch
* Create a Distributed Portgroup
* Attach the NFS datastore (if Selected) to the hosts
* Copy the [Photon OS](https://vmware.github.io/photon/) ISO image downloaded from [VMware's bintray server](https://dl.bintray.com/vmware/photon) to the datastore
* Create directories to add sample ports

First, edit settings in samples/vsphere/vcenter/setup/testbed.py and replace everything in < > brackets with your environment information. Leave the rest of the settings in this file at their default values.

```python
config["SERVER"]    = "<vcenter_hostname_or_ip>"
config["USERNAME"]  = "<vsphere_username>"
config["PASSWORD"]  = "<vsphere_password>"

config["ESX_HOST1"] = "<ESX_host1_ipaddress>"
config["ESX_HOST2"] = "<ESX_host2_ipaddress>"
config["ESX_USER"]  = "<esx_username>"
config["ESX_PASS"]  = "<esx_password>"

config["USE_NFS"]   = True
config["NFS_HOST"]  = "<nfs_ipaddress>"
config["NFS_REMOTE_PATH"] = "/store1"
```

At this point, we're ready to run the setup script: 

```cmd
$ python samples/vsphere/vcenter/setup/main.py -sv
```

After completion you will see from the output and also the vSphere Client that the environment has now been fully setup and is ready to easily run further samples.

To view other available command-line options:

```cmd
$ python samples/vsphere/vcenter/setup/main.py -h
```

#### Run the vAPI vCenter sample suite:

```cmd
$ python samples/vsphere/vcenter/setup/main.py -riv
```

#### Run a specific sample in a standalone mode:

```cmd
$ python samples/vsphere/vcenter/vm/list_vms.py -v
```

## API Documentation

### vSphere API Documentation

* [VMware vSphere REST API Reference documentation](https://developer.vmware.com/docs/vsphere-automation/latest/)
* [vSphere 8.0 U2 Python APIs (latest)](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.2.0/)
* Previous Releases:	vSphere [8.0 U1](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.1.0/)
[8.0 GA](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.0.1/)
[8.0.0.0](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.0.0/),
[7.0 U3](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/7.0.3.0/)
[7.0 U2](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/7.0.2.0/),   [7.0 U1](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/7.0.1.0/),   [7.0](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/7.0.0.1/).

### VMware Cloud on AWS API Documentation

* [VMware Cloud on AWS REST APIs](http://developers.eng.vmware.com/docs/vmc/latest/) 
* [VMware Cloud on AWS Console Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/vmc/index.html)
* [VMware Cloud on AWS Disaster Recovery as a Service (DRaaS) Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/vmc-draas/index.html)


### NSX API Documentation
* [NSX-T Data Center](https://docs.vmware.com/en/VMware-NSX-T-Data-Center/index.html)
* [NSX Manager Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/nsx/nsx/index.html) - API for managing NSX-T cluster and transport nodes for on-prem customers
* [NSX Policy Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/nsx/nsx_policy/index.html) - primary API for managing logical networks for on-prem customers
* [NSX VMC Policy Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/nsx/nsx_vmc_policy/index.html) - primary API for managing logical networks for VMC customers
* [NSX VMC AWS Integration Python APIs](https://vmware.github.io/vsphere-automation-sdk-python/nsx/nsx_vmc_aws_integration/index.html) - API for managing AWS underlay networks for VMC customers

## Troubleshooting

Common issues you may run into while installing the sdk and running samples are listed [here](https://github.com/vmware/vsphere-automation-sdk-python/wiki/Troubleshooting)

## Support

For official support, users with Premium SDK Support, Standard SDK Support and Premier/Success360 customers can reach out to [VMware Global Support](https://kb.vmware.com/s/article/87265?lang=en_US) for any issues.
For community support, please open a [Github issue](https://github.com/vmware/vsphere-automation-sdk-python/issues) or start a [Discussion](https://github.com/vmware/vsphere-automation-sdk-python/discussions)

## Repository Administrator Resources

### Board Members

Board members are volunteers from the SDK community and VMware staff members, board members are not held responsible for any issues which may occur from running of samples from this repository.

Members:
* Ankit Agrawal (VMware)
* Jobin George (VMware)
* Martin Tsvetanov (VMware)
* Shweta Purohit (VMware)
* Kunal Singh (VMware)

## VMware Resources

* [vSphere Automation SDK Overview](http://pubs.vmware.com/vsphere-65/index.jsp#com.vmware.vapi.progguide.doc/GUID-AF73991C-FC1C-47DF-8362-184B6544CFDE.html)
* [VMware Sample Exchange](https://code.vmware.com/samples) It is highly recommended to add any and all submitted samples to the VMware Sample Exchange
* [VMware Code](https://code.vmware.com/home)
* [VMware Developer Community](https://communities.vmware.com/community/vmtn/developer)
* VMware vSphere [REST API Reference documentation](https://developer.vmware.com/docs/vsphere-automation/latest/).
* [VMware Python forum](https://code.vmware.com/forums/7508/vsphere-automation-sdk-for-python)
