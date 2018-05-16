This directory contains samples for managing vSphere hybrid linked mode:

The sample were tested against vSphere 6.7

### Hybrid Linked Mode link Create/List/Delete operations
Sample                                                                | Description
----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
links_client.py                                                       | Demonstrates link Create, List, Delete operations with a foreign platform service controller in a different SSO domain.

### Hybrid Linked Mode Administrator identity source group Add/Get/Remove operations
Sample                                                                      | Description
----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------
administrator_client.py                                                     | Demonstrates Add, Get, Remove operations for a given SSO group in an Identity source to the CloudAdminGroup.

### Testbed Requirement:
    - 2 vCenter Server in different SSO domains. The 2nd vCenter should be on version 6.5x
    - The username being used to run the sample should have the HLM.Manage privilege.
    - AdministratorClient sample requires the vCenter under test to have an Identity Source added and a local group called CloudAdminGroup to be created.