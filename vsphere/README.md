This document describes the vSphere Automation Python SDK samples that use the vSphere Automation python client library. Additionally, some of the samples demonstrate the combined use of the vSphere Automation and vSphere APIs. To support this combined use, the vSphere Automation Python SDK samples require the vSphere Management SDK packages (pyVmomi) to be installed on the client. The examples have been developed to work with python 2.7, 3.3, 3.4 and 3.5.

The following table shows the sample sub-directories and their contents.

Directory                       | Description
------------------------------- | -------------
vsphere.samples.common          | Samples common classes and abstractions; This package does NOT contain any sample
vsphere.samples.vim.helpers	    | Samples and utilities for accessing and manipulating VC objects using pyVmomi
vsphere.samples.lookupservice   | Service discovery sample using lookup service APIs
vsphere.samples.vcenter	        | vAPI samples for managing vSphere infrastructure and virtual machines
vsphere.samples.workflow        |	Various vAPI work flow samples
vsphere.samples.inventory       |	Samples for inventory APIs for retrieving information about vCenter datastore and network objects.
