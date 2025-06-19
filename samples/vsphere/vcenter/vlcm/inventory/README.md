This directory contains below samples for inventory APIs:

1. Bulk Transition

   | Sample                     | Description                                                                 |
   |----------------------------|-----------------------------------------------------------------------------|
   | bulk_extract.py            | Demonstrates extracting clusters/standalone hosts in bulk                   |
   | bulk_extract_transition.py | Demonstrates extracting and transitioning clusters/standalone hosts in bulk |
   | bulk_transition.py         | Demonstrates transitioning clusters/standalone hosts in bulk                |

### Running the samples:

    #For example, you can use the following command to run transition on a group of clusters
    python vsphere-samples/vsphere-automation-sdk/samples/vsphere/vcenter/vlcm/inventory/bulk_transition/bulk_transition.py -s "<vcenter_ip>" -u "<user>" -p "<password>" -v --entityType "CLUSTER" --entities "domain-c11" "domain-c15"

### Testbed Requirement:

    - vCenter Server >= 9.0.0+
    - A datacenter
    - If a cluster is used as an entity, cluster should have at least one host.
    - Host with version >= 7.0.2
