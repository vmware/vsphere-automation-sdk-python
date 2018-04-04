# VMware vSphere Automation SDK for Python  
[![Build Status](https://travis-ci.com/vmware/vsphere-automation-sdk-python.svg?token=v9mEJjcpDiQ9DrYbzyaQ&branch=master)](https://travis-ci.com/vmware/vsphere-automation-sdk-python)

## Table of Contents
- [Abstract](#abstract)
- [Supported vCenter Releases](#supported-vcenter-releases)
- [VMware Cloud on AWS Support](#vmware-cloud-on-aws-support)
- [Quick Start Guide](#quick-start-guide)
- [Run SDK Samples](#run-sdk-samples)
- [API Documentation](#api-documentation)
- [Submitting samples](#submitting-samples)
- [Resource Maintenance](#resource-maintenance)
- [Repository Administrator Resources](#repository-administrator-resources)
- [VMware Resources](#vmware-resources)

## Abstract
This document describes the vSphere Automation Python SDK samples that use the vSphere Automation
python client library. Additionally, some of the samples demonstrate the combined use of the
vSphere Automation and vSphere APIs. To support this combined use, the vSphere Automation Python SDK
samples require the vSphere Management SDK packages (pyVmomi) to be installed on the client.
The samples have been developed to work with python 2.7.x and 3.3+

## Supported vCenter Releases
vCenter 6.0 and 6.5. 
Certain APIs and samples that are introduced in 6.5 release, such as vCenter, Virtual Machine and Appliance Management. Please refer to the notes in each sample for detailed compatibility information. 

## VMware Cloud on AWS Support
The VMware Cloud on AWS API and samples are currently available as a preview and are subject to change in the future.

## Quick Start Guide

### Prepare a Python Development Environment

We recommend you to install latest [Python](http://docs.python-guide.org/en/latest/starting/installation/) and
[pip](https://pypi.python.org/pypi/pip/) on your system.  

A Python virtual environment is also highly recommended.
* [Install a virtual env for Python 2](https://virtualenv.pypa.io/en/stable/)
* [Install a virtual env for Python 3](https://docs.python.org/3/tutorial/venv.html)

### Installing Required Python Packages

```cmd
git clone https://github.com/vmware/vsphere-automation-sdk-python.git
cd vsphere-automation-sdk-python
pip install --upgrade --force-reinstall -r requirements.txt --extra-index-url file:///`pwd`/lib
```

**NOTE:** The SDK also requires OpenSSL 1.0.1+ if you want to connect to vSphere 6.5+ in order to support TLS1.1 & 1.2

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
Python 3.6.3 (v3.6.3:2c5fed86e0, Oct  3 2017, 00:32:08)
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
Python 3.6.3 (v3.6.3:2c5fed86e0, Oct  3 2017, 00:32:08)
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

The API documentation can be found [here](doc/client.zip)

## Submitting samples

### Developer Certificate of Origin

Before you start working with this project, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on as an open-source patch.

### Sample Template

[Sample template](sample_template) contains boilerplate code that can be used to build a new sample.
Please copy the file and use it as a starting point to write a new sample.

### Required Information

The following information must be included in the README.md or in the sample docstring in case README already exists in same folder.
* Author Name
  * This can include full name, email address or other identifiable piece of information that would allow interested parties to contact author with questions.
* Minimal/High Level Description
  * What does the sample do ?
* Any KNOWN limitations or dependencies

### Suggested Information

The following information should be included when possible. Inclusion of information provides valuable information to consumers of the resource.
* vSphere version against which the sample was developed/tested
* SDK version against which the sample was developed/tested
* Python version against which the sample was developed/tested

### Contribution Process

* Follow the [GitHub process](https://help.github.com/articles/fork-a-repo)
  * Please use one branch per sample or change-set
  * Please use one commit and pull request per sample
  * Please post the sample output along with the pull request
  * If you include a license with your sample, use the project license

### Code Style

Please conform to pep8 standards. Check your code by running the pep8 tool.
    https://pypi.python.org/pypi/pep8

## Resource Maintenance
### Maintenance Ownership

Ownership of any and all submitted samples are maintained by the submitter.

### Filing Issues

Any bugs or other issues should be filed within GitHub by way of the repository’s Issue Tracker.

### Resolving Issues

Any community member can resolve issues within the repository, however only the board member can approve the update. Once approved, assuming the resolution involves a pull request, only a board member will be able to merge and close the request.

### VMware Sample Exchange

It is highly recommended to add any and all submitted samples to the VMware Sample Exchange:  <https://code.vmware.com/samples>

Sample Exchange can be allowed to access your GitHub resources, by way of a linking process, where they can be indexed and searched by the community. There are VMware social media accounts which will advertise resources posted to the site and there's no additional accounts needed, as the VMware Sample Exchange uses MyVMware credentials.     

## Repository Administrator Resources

### Board Members

Board members are volunteers from the SDK community and VMware staff members, board members are not held responsible for any issues which may occur from running of samples from this repository.

Members:
* Tianhao He (VMware)
* Steve Trefethen (VMware)

### Approval of Additions

Items added to the repository, including items from the Board members, require 2 votes from the board members before being added to the repository. The approving members will have ideally downloaded and tested the item. When two “Approved for Merge” comments are added from board members, the pull can then be committed to the repository.

## VMware Resources

* [vSphere Automation SDK Overview](http://pubs.vmware.com/vsphere-65/index.jsp#com.vmware.vapi.progguide.doc/GUID-AF73991C-FC1C-47DF-8362-184B6544CFDE.html)
* [VMware Code](https://code.vmware.com/home)
* [VMware Developer Community](https://communities.vmware.com/community/vmtn/developer)
* VMware vSphere [REST API Reference documentation](https://code.vmware.com/web/dp/doc/preview?id=4644).
* [VMware Python forum](https://code.vmware.com/forums/7508/vsphere-automation-sdk-for-python)
