This directory contains samples for Platform Service Controller, SSO and Lookup Service APIs:

The vSphere Automation SDK for Python samples use the vSphere Automation Lookup Service
to obtain the URLs for other vSphere Automation services (SSO, vAPI, VIM, SPBM, etc.).
The SDK contains the Lookup Service WSDL files. The samples use the python SUDS client
for accessing the lookup service. The Lookup Service WSDL files are located in wsdl/ directory.

Running the samples

    $ cd /path/to/vsphere-automation-sdk-python-samples/bin
    $ ./run_sample.sh ../samples/vsphere/sso/print_services.py --lswsdlurl file:///path/to/vsphere-automation-sdk-python-samples/samples/vsphere/sso/wsdl/lookupservice.wsdl --lssoapurl https://<sso_server>/lookupservice/sdk -v

* Testbed Requirement:
    - 1 vCenter Server
