This directory contains samples for Platform Service Controller, SSO and Lookup Service APIs:

The vSphere Automation SDK for Python samples use the vCenter Lookup Service
to obtain the URLs for other vSphere Automation services (SSO, vAPI, VIM, SPBM, etc.).
The SDK contains the Lookup Service WSDL files. The samples use the python SUDS client
for accessing the lookup service. The Lookup Service WSDL files are located in wsdl/ directory.

Running the samples
```cmd
$ python external_psc_sso_workflow.py --lsurl https://<server>/lookupservice/sdk -u 'administrator@vsphere.local' -p 'Admin!23' -v
```
* Testbed Requirement:
    - 1 vCenter Server
