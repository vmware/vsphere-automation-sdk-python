#vLCM/Cluster/HCL

This directory contains samples of cluster level vLCM HCL APIs.

The hardware compatibility service provides a way to ensure that the various driver and firmware components that are going to be installed on certain HW components (which are in use by vSAN) are certified against the ESXi version and present in the vSAN VCG.

The Hardware Compatibility Details provides information such as the overall compliance status of the cluster, the base image version, pci device compliance, and storage device compliance. Within the more specific sections of the hardware compatibility details, one can find the corresponding supported devices.

##Supported Features by Release:

    7.0 : IO Controllers
    7.0 U3 : IO Controllers, Directly Attached Storage Devices, Storage Devices Configured With RAID Controller
    8.0 : IO Controllers, Directly Attached Storage Devices, Storage Devices Configured With RAID Controller, Intel VMD NVMe, RDMA NIC

##APIs
GET Hardware Compatibility Details - Returns the HCL validation check detailed results.

##Running the Samples:

To view the available command-line options:

    $ python hw_compatibility_details_sample.py --help

Run the samples:

    $ python hw_compatibility_details_sample.py --server <Vcenter Server IP> --username <username> --password <password> --skipverification --cluster <MOID of cluster>
