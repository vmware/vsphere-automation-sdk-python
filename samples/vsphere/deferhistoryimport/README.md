This directory contains samples for the Defer History Data Import APIs. Defer History Data Import is a new
feature for the upgrade that allows historical data and performance metrics data to be imported in the background
after the upgrade is done, thus allowing shorter downtime for the whole upgrade process. The feature is only applicable
for upgrades or migrations from 6.0 and 6.5 with external database. For more information, please review the official
release notes.

The operations on the API are as follow:

    * status of defer history data import
    * pause defer history data import
    * resume defer history data import
    * cancel defer history data import

Overview of the directory code samples:

    * vc_import_history_sample.py - running a simple workflow to pause and resume
      Defer History Data Import that is still not completed.
    * vc_import_history_cli.py - allowing to trigger different parts of the API,
      showing example code structure.
    * vc_import_history_common.py - common functionality between the main files.

To view the available command-line options:

     $ python vc_import_history_sample.py --help

     $ python vc_import_history_cli.py --help

Running the samples:

    $ python vc_import_history_sample.py --server <vCenter Server IP> --username <username> --password <password>

Running the cli:

    $ python vc_import_history_cli.py --server <vCenter Server IP> --username <username> --password <password> --operation <operation>

The operation choice is as follows (information is also available using --help)

    * status
    * pause
    * resume
    * cancel

Testbed Requirement:

    * 1 vCenter Server appliance version 6.7 or above successfully upgraded using the option for transferring historical data after upgrade.
