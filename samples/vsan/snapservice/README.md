This directory contains samples for snapservice APIs:
1. Protection Group Create, List and Delete operations:
   Sample                               | Description
   -------------------------------------|---------------------------------------------------
   list_protection_groups.py            | Demonstrates listing protection groups
   create_protection_group.py           | Demonstrates creating protection group
   delete_protection_groups.py          | Demonstrates deleting protection groups

2. Protection Group Snapshot Delete operations:
   Sample                               | Description
   -------------------------------------|---------------------------------------------------
   delete_protection_group_snapshots.py | Demonstrates deleting protection group snapshots

### To view the available command-line options:
	$ python protection_group/list_protection_groups.py --help
	$ python protection_group/create_protection_group.py --help
	$ python protection_group/delete_protection_groups.py --help
	$ python snapshot/delete_protection_group_snapshots.py --help

### Running the samples:
	Fill "Snapservice protection group creation spec" section in vcenter/setup/testbed.py when calling create_pg.py

	$ python protection_group/list_protection_groups.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> -v

	$ python protection_group/create_protection_group.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> -v
	$ python protection_group/create_protection_group.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> -v -c

	$ python protection_group/delete_protection_groups.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> --pgnames <protection groups name to delete> -v
	$ python protection_group/delete_protection_groups.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> --pgnames <protection groups name to delete> -v --force

	$ python snapshot/delete_protection_group_snapshots.py --server <vCenter Server IP> --username <username> --password <password> --snapservice <snapservice IP> --cluster <cluster name> --pgname <protection group name to delete snapshot> --remain <snapshot remain> -v

### Testbed Requirement:
    - vCenter Server >= 8.0.3+
    - vSAN ESA disk
    - vSAN Cluster
    - Snapservice = 8.0.3