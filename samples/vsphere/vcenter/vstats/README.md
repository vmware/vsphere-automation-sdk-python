This directory contains samples for managing vSphere Stats platform and querying for stats data:

### vSphere Stats Discovery APIs - List Counters, List Counter Metadata, Get Resource Address Schema, List Providers, List Resource types, List Metrics, List Counter-sets
Sample                                                                      | Description
----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------
discovery.py                                                                | Demonstrates all vSphere Stats discovery APIs which give current state of the system.

### vSphere Stats Acquisition Specification Create/Get/List/Delete/Update operations
Sample                                                                      | Description
----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------
acquisitionspec/lifecycle.py                                                | Demonstrates create, get, list, update and delete operations of Acquisition Specifications.

### vSphere Stats End to End workflow - Create an Acquisition Specification and query for data points
Sample                                                                      | Description
----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------
data/query_data_points.py                                                   | Demonstrates creation of Acquisition Specification and query for data points filtered by cid.
data/query_data_points_set_id.py                                            | Demonstrates creation of Acquisition Specification using Counter SetId and query for data points filtered by resource.
data/query_data_points_with_predicate.py                                    | Demonstrates creation of Acquisition Specification using QueryPredicate "ALL" and query for data points filtered by cid.


To view the available command-line options:

    $ python discovery.py --help
    $ python acquisitionspec/lifecycle.py --help
    $ python data/query_data_points.py --help
    $ python data/query_data_points_set_id.py --help
    $ python data/query_data_points_with_predicate.py --help

Running the samples:

    $ python discovery.py --server <vCenter Server IP> --username <username> --password <password> --skipverification
    $ python acquisitionspec/lifecycle.py --server <vCenter Server IP> --username <username> --password <password> --skipverification --interval <interval> --expiration <expiration>
    $ python data/query_data_points.py --server <vCenter Server IP> --username <username> --password <password> --skipverification --interval <interval> --expiration <expiration>
    $ python data/query_data_points_set_id.py --server <vCenter Server IP> --username <username> --password <password> --skipverification --interval <interval> --expiration <expiration>
    $ python data/query_data_points_with_predicate.py --server <vCenter Server IP> --username <username> --password <password> --skipverification --interval <interval> --expiration <expiration>


### Testbed Requirement:
    - 1 vCenter Server on version 7.0x or higher
    - 2 ESXi hosts on version 7.0x or higher with VMs
    - 1 datastore
