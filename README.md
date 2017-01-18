# VMware vSphere Automation SDK for Python

## Table of Contents
- [Abstract](#abstract)
- [Quick Start Guide](#quick-start-guide)
  - [Setting up a vSphere Test Environment](#setting-up-a-vsphere-test-environment)
  - [Installing the required Python Packages](#installing-the-required-python-packages)
  - [Installing SDK Bundled Packages](#installing-sdk-bundled-packages)
  - [Running the SDK Sample Setup Script](#running-the-sdk-sample-setup-script)
  - [Running a complex sample](#running-a-complex-sample)
- [API Documentation and Programming Guide](#api-documentation-and-programming-guide)
- [Submitting samples](#submitting-samples)
- [Resource Maintenance](#resource-maintenance)
  - [Maintenance Ownership](#maintenance-ownership)
  - [Filing Issues](#filing-issues)
  - [Resolving Issues](#resolving-issues)
  - [VMware Sample Exchange](#vmware-sample-exchange)
- [Repository Administrator Resources](#repository-administrator-resources)
  - [Board Members](#board-members)
  - [Approval of Additions](#approval-of-additions)

## Abstract
This document describes the vSphere Automation Python SDK samples that use the vSphere Automation python client library. Additionally, some of the samples demonstrate the combined use of the vSphere Automation and vSphere APIs. To support this combined use, the vSphere Automation Python SDK samples require the vSphere Management SDK packages (pyVmomi) to be installed on the client. The examples have been developed to work with python 2.7, 3.3, 3.4 and 3.5.

## Quick Start Guide
This document will walk you through getting up and running with the Python SDK Samples. Prior to running the samples you will need to setup a vCenter test environment and install local Python packages, the following steps will take you through this process.

Before you can run the SDK samples we'll need to walk you through the following steps:

1. Setting up a vSphere test environment
2. Installing the required Python packages
3. Installing SDK provided packages
4. Running SDK Samples setup script

### Setting up a vSphere Test Environment
**NOTE:** The samples are intended to be run against a freshly installed **non-Production** vSphere setup as the scripts may make changes to the test environment and in some cases can destroy items when needed.

To run the samples a vSphere test environment is required with the following configuration
* 1 vCenter Server
* 2 ESX hosts
* 1 Datastore with at least 3GB of free capacity

Please have the details of these available but do not have any configuration pre-created on vCenter server or ESXi Hosts, for example there should be no existing datacenters, clusters or attached hosts on the vCenter server.

### Installing the required Python Packages
**Note:** The SDK requires Python v2.7 (preferably v2.7.12+) to run the setup/samples, please make sure you have the appropriate version installed before continuing. If you are on macOS/OSX/Linux, please note that the system installed version of Python may be outdated and/or not be intended for development and we recommended you [install Python](http://docs.python-guide.org/en/latest/starting/installation/) yourself before installing the required packages. [Virtualenv](https://virtualenv.pypa.io/en/stable/) is also highly recommended.

In this section we list the various packages which need to be installed using "pip install"; For more details on how to install python packages using pip please refer to the [pip user guide](http://pip.readthedocs.io/en/latest/user_guide/).

#### pyOpenSSL
pyOpenSSL requires the python cryptography packge to be installed. Please follow the detailed instructions [here](https://cryptography.io/en/latest/installation/) to install the cryptography package. VMware strongly recommends using openssl version **1.0.1j** or, higher. SDK and samples are tested against openssl version >= 1.0.1j.

pyOpenSSL version 0.14 is needed for the SDK (vapi_runtime) and samples.

    pip install pyopenssl

#### pyVmomi

This library is needed for accessing/manipulating vCenter Server managed objects using vSphere APIs; For more information please refer to vmware pyVmomi

    pip install pyvmomi

#### lxml
Please follow detailed instructions from [Installing lxml](http://lxml.de/installation.html) (for Windows refer to the section below on installation).

    pip install lxml

#### suds (suds-jurko)
This library is needed for lookup service queries; For more information please refer to [suds Documentation](https://fedorahosted.org/suds/wiki/Documentation)

    pip install suds

Use suds-jurko for python 3.x

    pip install suds-jurko

### Installing SDK Bundled Packages
To run the samples for Content Library and Tagging you will need to install these additional packages.

**Note:** You will need to update the package path below accordingly to point to your local SDK folder.

#### vapi_runtime, vapi_common_client and vapi_client_bindings
    pip install /path/to/VMware-vSphere-Automation-SDK-Python/lib/vapi_client_bindings-2.5.0.zip --find-links=/path/to/VMware-vSphere-Automation-SDK-Python/lib/

### Running the SDK Sample Setup Script
Before executing the samples we'll need to setup the vSphere test environment using one of the sample scripts. Before we run the script we'll need to edit one of the files and provide IP addresses for the various machine instances.

First, from the command line change to the SDK ./bin folder.

    $ cd /path/to/VMware-vSphere-Automation-SDK-Python-<version>/bin

Next, using a text editor open ../samples/src/vsphere/samples/vcenter/setup/testbed.py and edit the following settings replace everything in < > brackts with your environment information. Leave the rest of the settings in this file at their default values.

    config["SERVER"] = "<vcenter_hostname_or_ip>"
    config["USERNAME"] = "<vsphere_username>"
    config["PASSWORD"] = "<vsphere_password>"

    config["ESX_HOST1"] = "<ESX_host1_ipaddress>"
    config["ESX_HOST2"] = "<ESX_host2_ipaddress>"
    config["ESX_USER"] = "<esx_username>"
    config["ESX_PASS"] = "<esx_password>"

    config["USE_NFS"] = True
    config["NFS_HOST"] = "<nfs_ipaddress>"

Save and close the file. 

Next, on OSX/Linux we will ensure our setup script we use to run the samples is set to execute, run the following:

    $ chmod +x ./run_sample.sh

At this point, we're ready to run the setup script. 

This script will perform the following:
* Create 2 test Datacenters 
* Create a test Cluster
* Create Test Folders for VM Storage
* Attach the hosts
* Create a Distributed Switch
* Create a Distributed Portgroup
* Attach the NFS datastore (if Selected) to the hosts
* Copy the [Photon OS](https://vmware.github.io/photon/) ISO image downloaded from [VMware's bintray server](https://dl.bintray.com/vmware/photon) to the datastore
* Create directories to add sample ports


**Note:** The setup script may take several minutes to complete.

**To view the available command-line options:**

    $ ./run_sample.sh ../vsphere/samples/vcenter/setup/main.py -h

**To run the setup script:**

    $ ./run_sample.sh ../vsphere/samples/vcenter/setup/main.py -st

After completion you will see from the output and also the vSphere Webclient that the environment has now been fully setup and is ready to easily run further samples.

### Running a complex sample
This SDK includes a sample script which can be used to perform a number of actions and give you an indication of how to perform multiple vCenter actions, this script is located in the /vsphere/samples/vcenter/setup/ directory, use the following instructions to run this sample:

**Run the vAPI vCenter sample suite:**

    $ ./run_sample.sh ../vsphere/samples/vcenter/setup/main.py -rit

## API Documentation and Programming Guide
The API documentation for the samples can be found here : TODO

## Submitting samples
The following information must be included in the README.md (TODO: header of the file or a separate md file?) for each submitted sample.
* Author Name
  * This can include full name, email address or other identifiable piece of information that would allow interested parties to contact author with questions.
* Date
  * Date the sample was originally written
* Minimal/High Level Description
  * What does the sample do ?
* vSphere version against which the sample was developed/tested
* SDK version against which the sample was developed/tested
* Python version against which the sample was developed/tested
* Any KNOWN limitations or dependencies

## Resource Maintenance
### Maintenance Ownership
Ownership of any and all submitted samples are maintained by the submitter.
### Filing Issues
Any bugs or other issues should be filed within GitHub by way of the repository’s Issue Tracker.
### Resolving Issues
Any community member can resolve issues within the repository, however only the board member can approve the update. Once approved, assuming the resolution involves a pull request, only a board member will be able to merge and close the request.

### VMware Sample Exchange
It is highly recommended to add any and all submitted samples to the VMware Sample Exchange:  <https://developercenter.vmware.com/samples>

Sample Exchange can be allowed to access your GitHub resources, by way of a linking process, where they can be indexed and searched by the community. There are VMware social media accounts which will advertise resources posted to the site and there's no additional accounts needed, as the VMware Sample Exchange uses MyVMware credentials.     

## Repository Administrator Resources
### Board Members

Board members are volunteers from the SDK community and VMware staff members, board members are not held responsible for any issues which may occur from running of samples from this repository.

Members:

### Approval of Additions
Items added to the repository, including items from the Board members, require 2 votes from the board members before being added to the repository. The approving members will have ideally downloaded and tested the item. When two “Approved for Merge” comments are added from board members, the pull can then be committed to the repository.
