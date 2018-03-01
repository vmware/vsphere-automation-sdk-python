"""

Simple web form that creates VMs in a VMware Cloud on AWS SDDC

vCenter API documentation is available at https://code.vmware.com/apis/191/vsphere-automation

Matt Dreyer
August 15, 2017

You can install python 3.6 from https://www.python.org/downloads/windows/

You can install the dependent python packages locally (handy for Lambda) with:
pip install requests -t . --upgrade
pip install simplejson -t . --upgrade
pip install certifi -t . --upgrade
pip install pyvim -t . --upgrade


"""

import requests                         #need this for Get/Post/Delete
import certifi                          #need this for HTTPS
import simplejson as json               #need this for JSON
import uuid                             #need this to automatically name newly created VMs


# To use this script you need to create an OAuth Refresh token for your Org
# You can generate an OAuth Refresh Token using the tool at vmc.vmware.com
# https://console.cloud.vmware.com/csp/gateway/portal/#/user/tokens
strAccessKey = "your key goes here"


#where are our service end points
strProdURL = "https://vmc.vmware.com"
strCSPProdURL = "https://console.cloud.vmware.com"

  


def getAccessToken(myKey):
    params = {'refresh_token': myKey}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    json_response = response.json()
    access_token = json_response['access_token']

    # debug only
#    print(response.status_code)
#    print(response.json())	    
    
    return access_token

    
	
#-------------------- Figure out which Org we are in
def getTenantID(sessiontoken):

    myHeader = {'csp-auth-token' : sessiontoken}

    response = requests.get( strProdURL + '/vmc/api/orgs', headers=myHeader)

# debug only
#    print(response.status_code)
#    print(response.json())	
	
# parse the response to grab our tenant id
    jsonResponse = response.json()
    strTenant = str(jsonResponse[0]['id'])
	
    return(strTenant)

    
#---------------Login to vCenter and get an API token
# this will only work if the MGW firewall rules are configured appropriately
def vCenterLogin(sddcID, tenantid, sessiontoken):

    #Get the vCenter details from VMC
    myHeader = {'csp-auth-token' : sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + tenantid + "/sddcs/" + sddcID
    response = requests.get(myURL, headers=myHeader)
    jsonResponse = response.json()

    vCenterURL = jsonResponse['resource_config']['vc_ip']
    vCenterUsername = jsonResponse['resource_config']['cloud_username']
    vCenterPassword = jsonResponse['resource_config']['cloud_password']

    
    #Now get an API token from vcenter
    myURL = vCenterURL + "rest/com/vmware/cis/session"
    response = requests.post(myURL, auth=(vCenterUsername,vCenterPassword))
    token = response.json()['value']
    vCenterAuthHeader = {'vmware-api-session-id':token}

    return(vCenterURL, vCenterAuthHeader)

	
 
 #------------ Create a VM from an OVF stored in Content Library

def createVM(sddcID, tenantid, sessiontoken, vmID, vmName):
 
    #first we need to get an authentaction token from vCenter
    vCenterURL, vCenterAuthHeader = vCenterLogin(sddcID, tenantid, sessiontoken)

    #Lets give our cow a name
    vmname = vmName + "-" + str(uuid.uuid4())
    
    #now lets create a VM from an OVF template stored in the Content Library
    #first we need to create a deployment spec
    deploymentspec = { \
       "target": { \
         "resource_pool_id": "resgroup-55", \
         "host_id": "host-31", \
         "folder_id": "group-v52" \
       }, \
       "deployment_spec": { \
             "name": vmname, \
             "accept_all_EULA": "true", \
             "storage_mappings": [ \
               { \
                 "key": "dont-delete-this-key", \
                 "value": { \
                   "type": "DATASTORE", \
                   "datastore_id": "datastore-61", \
                   "provisioning": "thin" \
                 } \
               } \
             ], \
             "storage_provisioning": "thin", \
             "storage_profile_id": "aa6d5a82-1c88-45da-85d3-3d74b91a5bad", \
        } \
     }
 
    print("\nPlease wait, VM deployment is in process....")
    
    myURL = vCenterURL + "rest/com/vmware/vcenter/ovf/library-item/id:" + vmID + "?~action=deploy"        
    response = requests.post(myURL, headers=vCenterAuthHeader, json=deploymentspec, timeout=None)
    #print(response.status_code)
    #print(response.text)
 
    if response.status_code == 200:
        print("Succesfully created a VM named: " + vmname )
    else:
        print("Failed to create a VM \n" + response.text)
    return(vmname)
    
    
#--------------------------------------------
#---------------- Main ----------------------
#--------------------------------------------
def lambda_handler(event, context):

    
    sddcID = "your sddc id goes here"
    tenantID = "your tenant id goes here"

	#Get our access token
    sessiontoken = getAccessToken(strAccessKey)

    
	#get our tenant ID if it wasn't hard coded at the top of the file
    if tenantID == "":
        tenantID = getTenantID(sessiontoken)
        
    #grab the form input
    vmType = event['vmtype']
    emailAddress = event['emailaddress']
    username = event['username']
    vmName = emailAddress
        
    #create a vm based on web form input
    print("starting vm creation process for " + vmName)
    
    vmName = createVM(sddcID, tenantID, sessiontoken, vmType, vmName)
    
    print("created vm named: " + vmName)
    
    feedback = "Congratulations, your VM named (" + vmName + ") is ready!"

    return(feedback)
    
#testing only
#lambda_handler({'username': 'Matt Dreyer', 'emailaddress': 'matt.dreyer@gmail.com', 'vmtype': '40ff3b8c-f6c7-4aa3-8db8-bb631e16ffae'}, 0)