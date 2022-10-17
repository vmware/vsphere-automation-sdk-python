This Directory contains samples for Patching API - applmgmt APIs
For more information, please review the official release notes.

Applmgmt having the followings APIs:
    * Pending: Performs patching for pending updates
    * Update: Status of update operation

Overview of the directory code samples:

    * update_sample.py - running a simple workflow to update the vc/component . It's having below APIs.
    GET https://{server}/rest/appliance/update/pending
    GET https://{server}/rest/appliance/update/pending/{{update_id}}/components
    GET https://{server}/rest/appliance/update/pending/{{update_id}}?component={component}
    POST https://{server}/rest/appliance/update/pending/{{update_id}}?action=precheck
    POST https://{server}/rest/appliance/update/pending/{{update_id}}?action=validate
    POST https://{server}/rest/appliance/update/pending/{{update_id}}?action=stage
    POST https://{server}/rest/appliance/update/pending/{{update_id}}?action=install


To view the available command-line options:

     $ python update_sample.py --help

Running the samples:

    $ python update_sample.py --server <vCenter Server IP> --username <username> --password <password> --url <customurl> --component <component> --skipverification


Testbed Requirement:

    * vCenter Server appliance version 8.0 or above are supported for component update.
    * vCenter Server appliance version 6.7 or above are supported for full patch.