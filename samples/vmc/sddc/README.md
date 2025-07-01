This directory contains samples for VMC SDDC APIs:

Sample | Description | Prerequisites
:--- | :--- | :---
add_remove_hosts.py | Demonstrates add and remove ESX hosts | A SDDC in the organization
connect_to_vsphere_with_default_sddc_password.py | Demonstrates how to connect to a vSphere in a SDDC using the initial cloud admin credentials. | A firewall rule to access the vSphere
deploy_ovf_template.py | Demonstrates the workflow to deploy an OVF library item to a resource pool in VMware Cloud on AWS. | An existing library item with an OVF template and an existing resource pool with resources for deploying the VM.
ovf_import_export_cloud.py | Demonstrates the workflow to import an OVF package into the content library, as well as download of an OVF template from the content library. | An existing vCenter DS with available storage.
sddc_crud.py | Demonstrates create and delete a SDDC | An organization associated with the calling user.