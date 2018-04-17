This directory contains samples for Backup Restore APIs:

    * List all backup jobs
    * CRUD operations on backup schedule

Running the samples

    $ python <sample-dir>/<sample>.py --server <vCenter Server IP> --username <username> --password <password> <additional-sample-parameters>

The additional sample parameters are as follows (all parameters can be displayed for any sample using option --help)

    * backup_schedule.py --location <location URL> --location_user <location-user> location_password <location-password>

* Testbed Requirement:
    - 1 vCenter Server
    - Backup server reachable through any of the supported protocols FTP/FTPS/SCP/HTTP/HTTPS
