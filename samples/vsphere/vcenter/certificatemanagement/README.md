This directory contains samples for managing the MACHINE SSL certificate and the TRUSTED ROOT CHAINS

The sample were tested against vSphere 7.0+

### TRUSTED ROOT CHAINS Create/List/Delete/Get operations
Sample                                                                | Description
----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
trusted_root_chains_create.py                                         | Demonstrates creation of the trusted root chain in vCenter.
trusted_root_chains_list.py                                           | Demonstrates listing of the aliases of the published trusted root chains in vCenter.
trusted_root_chains_delete.py                                         | Demonstrates deletion of the trusted root chain corresponding to the provided alias.
trusted_root_chains_get.py                                            | Demonstrates retrieval of the trusted root chain corresponding to the provided alias.

### Tls certificate Renew/Get/Replace/Replace with VMCA operations
Sample                                                                | Description
----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------
replace_tls_certificate.py                                            | Demonstrates replacement of the machine ssl certificate with a custom certificate signed by a third party CA.
renew_tls_certificate.py                                              | Demonstrates renewal of the machine ssl certificate for the given duration of time.
get_tls_certificate.py                                                | Demonstrates retrieval of the machine ssl certificate along with the X.509 certificate fields.
replace_tls_certificate_with_vmca_signed.py                           | Demonstrates replacement of the machine ssl certificate with a VMCA signed certificate.

### VMCA ROOT replace operation
Sample                                                                | Description
----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------
replace_vmca_root.py                                                  | Demonstrates replacement of the VMCA root certificate and regeneration of all the other certificates.

### Testbed Requirement:
    - 1 vCenter Server on version 7.0+
    - The username being used to run the sample should have either the CertificateManagement.Manage or
      the CertificateManagement.Administer privilege depending on the operation which is intended to be performed.
