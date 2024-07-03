This directory contains sample for getting TPM information using Trust Authority APIs added in __vcenter_version__ = '8.0+'
    * Get ESX TPM information   -  tpm_info.py

Running the samples
    $ python <sample-dir>/<sample>.py --server <vCenter Server IP> --username <username> --password <password> <additional-sample-parameters>

* Testbed Requirement:
    - 1 vCenter Server
    - 1 ESX host with TPM enabled

* Sample output
python samples/vsphere/hardwaretpm/tpm_info.py -s <vCenter Server IP> -u <username> -p <password> --skipverification
vcenter server = <ip>
vc username = <username>
----------------------------
TPM Information
----------------------------
'major_version: 2'
'minor_version: 0'
'active: True'
'manufacturer: NTC'
'model: rls'
'firmware_version: 1.3.1.0'
----------------------------
----------------------------
TPM Endorsement key
----------------------------
('-----BEGIN PUBLIC KEY-----\n'
 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1I65uMJU5MugQzl3K6yg\n'
 'Zjzed6aP7MX1Cl670NsvMSXs4FRdNZ1wkJHFUHrSG6ihBmHoziqWKhMjv3g9qrmJ\n'
 'tGR6uGsDi2nFsjn0/AK5epDQsQC6FffE6OotqAMtx+MocuU6XOacZ0lyjUcVGZRX\n'
 'RLK1TmRL3ugupFDe0XLcQZPNzv4cYNLub3prYEgEcpac89xVEn/TCyRK/nMGTHxs\n'
 'Z1oMI+FjpKMh5Vj/6c2gwhoX7tYQFXZOLy6S9prok5fWgHssZAjQNLjp1rihVpp3\n'
 '6BIkCBRw+LSEdz47naOsZN7NEYO78It3JGlPt2fpYVJ6+/8ObUa5Sv8svzFOb0Qq\n'
 'rQIDAQAB\n'
 '-----END PUBLIC KEY-----\n')
----------------------------
