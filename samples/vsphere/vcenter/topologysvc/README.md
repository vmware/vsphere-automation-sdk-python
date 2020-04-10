This directory contains samples for getting vCenter Server replication status and node information

The samples are compatible with vSPhere 7.0+

### vCenter server node topology information List/Get operations
Sample                                                                | Description
----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
get_node.py                                                           | Demonstrates getting the vCenter Server or Platform service controler node information.
list_nodes.py                                                         | Demonstrates listing of the vCenter Server or Platform service controller node's information in Link Mode in an SSO Domain.
list_embedded_nodes.py                                                | Demonstrates listing of Embedded vCenter Server node's information in an SSO Domain.

### vCenter server Replication Status List operations
Sample                                                                | Description
----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------
list_replication_status.py                                            | Demonstrates listing of replication status of all vCenter Server's in an SSO Domain.
list_node_replication_status.py                                       | Demonstrates status of replication for a vCenter Server.

### Testbed Requirement:
    - 1 vCenter Server on version 7.0+
    - The username being used to run the sample should have System.Read privilege for the operation to be performed.
