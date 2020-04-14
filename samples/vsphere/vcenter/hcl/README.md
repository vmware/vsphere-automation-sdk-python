This directory contains samples for the ESXi Hardware Compatibility APIs. ESXi Hardware Compatibility feature generates a hardware compatibility report for a given ESXi against a target ESXi version.

For more information, please review the official release notes.

The feature is realized with the following APIs:
    * Compatibility Data Download: Updates the local compatibility data on the vCenter based on the latest version in the VMware Official repository.
    * Compatibility Data Status: Provides information about when the compatibility Datastore on the vCenter was last synced with VMware Official Repository.
    * Compatibility Releases : Lists the available ESXi releases for a given host that can be used to generate a compatibility report.
	* Compatibility Report: Generates a compatibility report for the source host against the target version.

Overview of the directory code samples:
    * compatibility_data_update_sample.py - Corresponds to Compatibiliy Data download operation as mentioned above.
    * compatibility_data_status_sample.py - Corresponds to Compatibiliy Data status as mentioned above.
    * compatibility_releases_sample.py - Corresponds to Compatibility Releases operation as mentioned above.
    * compatibility_report_sample.py - Corresponds to Compatibility Report operation as mentioned above.

To view the available command-line options:

     $ python compatibility_data_update_sample.py --help
     $ python compatibility_data_status_sample.py --help
     $ python compatibility_releases_sample.py --help
	 $ python compatibility_report_sample.py --help

Running the samples:

    $ python compatibility_data_update_sample.py --server <vCenter Server IP> --username <username> --password <password> --skipverification
    $ python compatibility_data_status_sample.py --server <vCenter Server IP> --username <username> --password <password> --skipverification
    $ python compatibility_releases_sample.py --server <vCenter Server IP> --username <username> --password <password> --host <MOID of the host> --skipverification
    $ python compatibility_report_sample.py --server <vCenter Server IP> --username <username> --password <password> --host <MOID of the host> --release <Target ESXi release> --skipverification

Testbed Requirement:

    * 1 vCenter Server appliance version 7.0 or above are supported.
