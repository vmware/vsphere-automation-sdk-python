This directory contains samples for log forwarding APIs:

    * Create log forwarding configurations
    * View log forwarding configurations
    * Update log forwarding configurations
    * Test log forwarding configurations

To view the available command-line options:

    $ python logforwarding/logforwarding.py --help

Running the samples:

    $ python logforwarding/logforwarding.py --server <vCenter Server IP> --username <username> --password <password> --loghost <log host> --port <log host port> --protocol <log protocol>

* Testbed Requirement:
    - 1 vCenter Server
    - Log host listening to syslog packets over any of the supported protocols UDP/TCP/TLS
