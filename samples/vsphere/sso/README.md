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

### Deprecation Notice
Starting vCenter server release 7.0, External Platform Services Controller (PSC) is no longer supported. All PSC services are consolidated into vCenter Server.
https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.vcenter.configuration.doc/GUID-135F2607-DA51-47A5-BB7A-56AD141113D4.html
In view of the above, related samples (ex: external_psc_sso_workflow) and other related files are deprecated and will be removed in next major SDK release.

Consequently, lookupservice WSDL files will also be removed in next major SDK release. Use well known URL path (https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-apis-sdks-introduction/GUID-B625C8FE-5E15-4918-98C0-69313E5880FB.html) instead of lookupservice.

For SSO, service endpoint is: "https://{domain}/STS/STSService"
https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-apis-sdks-introduction/GUID-5384662C-CD05-4CAE-894E-972F14A7ECB7.html

### Package Dependency Note
To run the deprecated samples, users need "Deprecated" package installed in their environment. 
https://pypi.org/project/Deprecated/
