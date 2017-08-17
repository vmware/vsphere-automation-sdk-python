This directory contains samples for the vSphere infrastructure and virtual machine APIs. You have two options to run samples inside this package:

* Run all samples under vcenter folder using main.py in samples.vsphere.vcenter.setup package. Please see the [README](../../../README.md#running-a-complex-sample) for more details.

* Run an individual sample in an existing environment. You can either pass the environment parameters through command line arguments or specify them in testbed.py in the setup package.
 
   For example, to run the create_default_vm sample in the vsphere.samples.vcenter.vm.create package:

      * with the testbed settings specified in testbed.py in a Linux machine:

         $ python samples/vsphere/vcenter/vm/create/create_default_vm.py -v

      * Or specify the credentials using command line parameters:

         $ python samples/vsphere/vcenter/vm/create/create_default_vm.py -s <server> -u <username> -p <password> -v
