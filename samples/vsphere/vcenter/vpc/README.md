This directory contains samples for VPC(Virtual Private Clouds) related APIs.

1. Connect network adapter to subnet - vm_connect_to_subnet.py

2. List/Get project/vpc/subnet:
    * List All existing project/vpc/subnet      - list_all.py
    * List or Get existing project(s)           - project.py
    * List or Get existing vpc(s)               - vpc.py
    * List or Get existing subnet(s)            - subnet.py


Command examples
================
Connect network adapter to a specific subnet:
python3 samples/vsphere/vcenter/network/vpc/vm_connect_to_subnet.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --vm_name VM-01 --subnet_id '/projects/default/vpcs/VPC-01/subnets/subnet-01'


List the project, VPC, and subnet:
python3 samples/vsphere/vcenter/network/vpc/list_all.py --server {vc_ip} --username {vc_user} --password {vc_passwd}


List the project according to the filter criteria:
python3 samples/vsphere/vcenter/network/vpc/project.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method list --names 'Virtual Private Clouds','project-01','project-02' --ids 'default','project-01','project-02' --external_ids '/projects/default'

Fetch a specific project:
python3 samples/vsphere/vcenter/network/vpc/project.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method get --proj_id 'default'


List the vpc according to the filter criteria:
python3 samples/vsphere/vcenter/network/vpc/vpc.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method list --proj_id 'default' --names 'VPC-01','VPC-02' --ids 'VPC-01','VPC-02' --external_ids '/projects/default/vpcs/VPC-01'

Fetch a specific vpc:
python3 samples/vsphere/vcenter/network/vpc/vpc.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method get --proj_id 'default' --vpc_id 'VPC-01'


List the subnet according to the filter criteria:
python3 samples/vsphere/vcenter/network/vpc/subnet.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method list --proj_id 'default' --vpc_id 'VPC-01' --names 'subnet-01','subnet-02' --ids 'subnet-01','subnet-02' --external_ids '/projects/default/vpcs/VPC-01/subnets/subnet-01'

Fetch a specific subnet:
python3 samples/vsphere/vcenter/network/vpc/subnet.py --server {vc_ip} --username {vc_user} --password {vc_passwd} --method get --proj_id 'default' --vpc_id 'VPC-01' --subnet_id 'subnet-01'