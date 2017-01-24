This directory contains sample scripts to setup the testbed required to run
the vCenter APIs samples. You can also use main.py to run all the samples
inside the vcenter.vm package.

* Testbed Requirement:
    - 1 vCenter Server
    - 2 ESX hosts
    - 1 NFS datastore with at least 3G free capacity.

* Prepare testbed using setup script:
    - Edit testbed.py with your settings. In particular, you need to set the IP addresses and credentials in this file.
    $ cd /path/to/VMware-vSphere-Automation-SDK-Python-<version>/client/bin
    $ ./run_sample.sh ../samples/vsphere/vcenter/setup/main.py -st

* Run the vAPI vCenter sample suite:
    $ ./run_sample.sh ../samples/vsphere/vcenter/setup/main.py -rit

* To check available options:
    $ ./run_sample.sh ../samples/vsphere/vcenter/setup/main.py -h
