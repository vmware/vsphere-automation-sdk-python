## Grant types available

| sample | grant_type |
| ------ | ------ |
| list_vms_authotization_code.py | authorization_code |
| list_vms_client_credentials.py | client_credentials | 
| list_vms_refresh_token.py | refresh_token |
| list_vms_password.py | password |

## Login Steps
1.  From a given VC IP/hostname, find the Identity Provider (sample available at [list_external_identity_providers.py](https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/oauth/list_external_identity_providers.py))
2.  Make a note of the auth/discovery/token endpoints from the identity provider object
3.  Get access token by making the call to endpoints based on parameters relevant to different grant types
4.  Convert access token to saml token (sample avaialble at [exchange_access_id_token_for_saml.py](https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/oauth/exchange_access_id_token_for_saml.py))
5.  Use this saml assertion to login to vCenter as a bearer token


## Executing the samples
vCenter needs to be registered with an Identity Provider. Applicable for VC 7.0+
### list_vms_authorization_code.py
Create an OAuth app and make a note of the *app_id*, *app_secret* and *redirect_uri*

First start the webserver code at [webserver.py](https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/oauth/grant_types/webserver.py). Note, this server is not recommended in a production setting, this is only to demonstarte the sample workflow

`$ python3 webserver.py`

Run the sample,

`$ python list_vms_authorization_code.py --server <VC_IP> --client_id <client_id> --client_secret <client_secret> --org_id <org_id> --skipverification`

### list_vms_client_credentials.py
Create an OAuth app and make a note of the *client_id* and *client_secret*

Run the sample,

`$ python list_vms_client_credentials.py --server <VC_IP> -- client_id <client_id> --client_secret <client_secret> --skipverification`

### list_vms_refresh_token.py
Use the *refresh_token* that was returned along with the access token in authorization_code workflow

Run the sample,

`$ python list_vms_refresh_token.py --server <VC_IP> --client_id <client_id> --client_secret <client_secret> --refresh_token <refresh_token> --skipverification`

### list_vms_password.py
Obtain access token using *username* and *password*

Run the sample,

`$ python list_vms_password --server <VC_IP> --username <username> --password <password> --skipverification`


## References
[Understanding vCenter Server Identity Provider Federation](https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.authentication.doc/GUID-0A3A19E6-150A-493B-8B57-37E19AB420F2.html)
