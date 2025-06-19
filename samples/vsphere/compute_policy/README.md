# Compute Policy API samples

This directory contains samples for the Compute Policy APIs.

## Compute Policy workflow
`compute_policy_workflow.py` uses the compute policy APIs to create a policy of VM-Host affinity capability and checks the compliance status of the policy for a particular virtual machine after the virtual machine is powered on.

`vcls_policy_workflow.py` uses the compute policy APIs to create a policy of vCLS VMs anti-affinity capability and checks the compliance status of the policy for a particular virtual machine after the virtual machine is powered on.

## Testbed requirements
- 1 vCenter server.
- 1 cluster on the vCenter server with DRS enabled.
- At least 2 hosts and 1 virtual machine in the cluster.
- A tag that can be associated with virtual machines and a tag that can be associated with hosts. Please refer to the [tagging samples](https://github.com/vmware/vsphere-automation-sdk-python/tree/master/samples/vsphere/tagging) for more information on creating categories, tags and tag associations.

## Running the sample for compute_policy_workflow.py
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


## Running the sample for vcls_policy_workflow.py
```
python3 samples/vsphere/compute_policy/vcls_policy_workflow.py    \
-s <vcenter-ip>                                                   \
-u <username>                                                     \
-p <password>                                                     \
-v -c                                                             \
-n <name-for-the-policy>                                          \
-vn <name-of-the-vm>                                              \
-vt <name-of-the-tag-that-can-be-associated-with-vms>             \
```


##### Sample output
```
vcenter server = 10.182.185.204
vc username = administrator@vsphere.local
Found VM 'hana-vm1' (vm-61)
Creating a vCLS VM anti-affinity policy
Policy created with id: 5fd61430-b3a6-456c-89f7-d4c853a4fe9c
Powering on hana-vm1
The compliance status of policy 5fd61430-b3a6-456c-89f7-d4c853a4fe9c for virtual machine vm-61 is UNKNOWN
Deleting the policy 5fd61430-b3a6-456c-89f7-d4c853a4fe9c
Powering off hana-vm1
```
