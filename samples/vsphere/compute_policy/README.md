# Compute Policy API samples

This directory contains samples for the Compute Policy APIs.

## Compute Policy workflow
`compute_policy_workflow.py` uses the compute policy APIs to create a policy of VM-Host affinity capability and checks the compliance status of the policy for a particular virtual machine after the virtual machine is powered on.

## Testbed requirements
- 1 vCenter server.
- 1 cluster on the vCenter server with DRS enabled.
- At least 2 hosts and 1 virtual machine in the cluster.
- A tag that can be associated with virtual machines and a tag that can be associated with hosts. Please refer to the [tagging samples](https://gitlab.eng.vmware.com/vapi-sdk/vsphere-automation-sdk-python/tree/cloud/samples/vsphere/tagging) for more information on creating categories, tags and tag associations.

## Running the sample
```
python3 samples/vsphere/compute_policy/compute_policy_workflow.py \
-s <vcenter-ip>                                                   \
-u <username>                                                     \
-p <password>                                                     \
-v -c                                                             \
-n <name-for-the-policy>                                          \
-vn <name-of-the-vm>                                              \
-vt <name-of-the-tag-that-can-be-associated-with-vms>             \
-hn <host-name>                                                     \
-ht <name-of-the-tag-that-can-be-associated-with-hosts>           \
```

##### Sample output
```
vcenter server = 10.192.174.79
vc username = Administrator@vsphere.local
Found VM 'vm_1' (vm-31)
Creating a VM-Host affinity policy
Policy created with id: 46e6c0a6-135c-4bfe-82ee-b1938128b5b9
Powering on vm_1
The compliance status of policy 46e6c0a6-135c-4bfe-82ee-b1938128b5b9 for VM vm-31 is COMPLIANT
Deleting the policy 46e6c0a6-135c-4bfe-82ee-b1938128b5b9
Powering off vm_1
```
