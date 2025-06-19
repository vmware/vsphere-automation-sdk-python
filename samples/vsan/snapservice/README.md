This directory contains below samples for snapservice APIs:

1. Cluster pair

   | Sample                 | Description                                  |
   |------------------------|----------------------------------------------|
   | create_cluster_pair.py | Demonstrates creating cluster pair           |
   | delete_cluster_pair.py | Demonstrates deleting cluster pair           |
   | cluster_pairs.py       | Demonstrates listing/getting cluster pair(s) |

2. Clusters
   
   | Sample                                                  | Description                                                                         |
   |---------------------------------------------------------|-------------------------------------------------------------------------------------|
   | clusters/protection_groups/protection_groups.py         | Demonstrates listing/getting/updating/pausing/resuming/deleting protection group(s) |
   | clusters/protection_groups/create_protection_group.py   | Demonstrates creating a protection group                                            |
   | clusters/protection_groups/pg_snapshots/pg_snapshots.py | Demonstrates listing/getting protection group snapshot(s)                           |
   | clusters/virtual_machines/query_virtual_machines.py     | Demonstrates querying virtual machines                                              |
   | clusters/virtual_machines/vm_snapshots/vm_snapshots.py  | Demonstrates listing/getting virtual machine snapshot(s)                            |

3. Info
   
   | Sample       | Description            |
   |--------------|------------------------|
   | info/info.py | Demonstrates info APIs |

4. Sites
   
   | Sample                                 | Description                                  |
   |----------------------------------------|----------------------------------------------|
   | sites/add_site.py                      | Demonstrates adding site                     |
   | sites/delete_site.py                   | Demonstrates deleting site                   |
   | sites/probe_connection.py              | Demonstrates probing connection              |
   | sites/probe_connection_with_vc_cert.py | Demonstrates probing connection with vc cert |
   | sites/sites.py                         | Demonstrates listing sites                   |

5. Tasks
   
   | Sample               | Description                 |
   |----------------------|-----------------------------|
   | tasks/get_task.py    | Demonstrates getting task   |
   | tasks/query_tasks.py | Demonstrates querying tasks |
   | tasks/task_utils.py  | Demonstrates task utils     |

### To view the available command-line options:

    $ python samples/vsan/snapservice/<the-sample-file> --help

### Running the samples:

    # Fill "Snapservice protection group creation spec" section in vcenter/setup/testbed.py then run the commands
    # For example, you can use the following command to run the list protection groups sample
    $ python samples/vsan/snapservice/clusters/protection_groups/protection_groups.py --server <vcenter_host> --snapservice <snapservice_host> --username <username> --password <password>  --cluster <cluster_name> --action list --skipverification

### Testbed Requirement:

    - vCenter Server >= 8.0.3+
    - vSAN ESA disk
    - vSAN Cluster
    - Snapservice = 9.0.0
