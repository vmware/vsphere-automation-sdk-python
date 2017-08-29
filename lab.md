# VMworld 2017 Python SDK Hackathon

## Install Python
Go to: [downloads](https://www.python.org/downloads/) and download and install Python for your Platform.
The SDK supports both python2 and python3, but we recommend to install the latest version of python3. 

## Setup Python SDK

Create and activate a virtual env:

#### Python2: 

    virtualenv <env_dir>

#### Python3:

| Windows | OSX |
|---------|-----|
|```py -m venv <env_dir>```|```python3 -m venv <env_dir>```|

#### Activate your virtual env:

| Windows | OSX |
|---------|-----|
|```<env_dir>\Scripts\activate```|```source <env_dir>/bin/activate```|

##  Clone the github repo
The python github repo is located [here](https://github.com/vmware/vsphere-automation-sdk-python)

```bash
git clone https://github.com/vmware/vsphere-automation-sdk-python
```
Or optionally [download](https://github.com/vmware/vsphere-automation-sdk-python/archive/master.zip) the SDK from Github as a .zip file and unzip it to the current dir.

##  Install dependencies

```bash
cd <sdk-dir>
pip install -r requirements.txt
```

## Set PYTHONPATH to use SDK helper methods  

#### Linux/Mac:

    export PYTHONPATH=${PWD}:$PYTHONPATH

#### Windows:

    set PYTHONPATH=%cd%;%PYTHONPATH%

## OPTIONAL: Install Visual Studio Code IDE
Microsoft's Visual Studio Code is a great (free) IDE that can be used for Python via a plugin providing a rich development environment.

[Visual Studio Code](https://code.visualstudio.com/)<br />
[Python Plugin](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python)

## vSphere Python SDK Examples
Start the Python command interpreter:

#### Linux/Mac:

    python3

#### Windows:

    py

## List VC inventory in interactive mode

### Connect to the vSphere REST API endpoint

```python
from samples.vsphere.common import vapiconnect
stub_config = vapiconnect.connect("<VC_IP_Address>", "administrator@vsphere.local", "VMware1!", True)
```

### List VMs

```python
from com.vmware.vcenter_client import VM
vm_svc = VM(stub_config)
vm_svc.list()
```

### List Datacenters

```python
from com.vmware.vcenter_client import *
Datacenter(stub_config).list()
```

### List Clusters

```python
Cluster(stub_config).list()
```

### List Hosts

```python
Host(stub_config).list()
```

### List Folders

```python
Folder(stub_config).list()
```

### List Datastore

```python
Datastore(stub_config).list()
```

### Find a specific host using a filter spec

```python
filter_spec = Host.FilterSpec(names=set(["<HOST_IP_Address>"]))
Host(stub_config).list(filter_spec)
```

Note: To exit interactive Python simply type quit() and press Return:

```python
quit()
```

## Run samples on github
For this portion of the lab we recommend using your favorite code editor or as mentioned above download and install [Visual Studio Code](https://code.visualstudio.com/). We will be using Visual Studio code to demo these examples.

Open the sample property file testbed.py using your favourite text editor, such as:

#### Linux/OSX:

```bash
vi samples/vsphere/vcenter/setup/testbed.py
```

#### Windows:

```shell
notepad samples\vsphere\vcenter\setup\testbed.py
```

And then change the following two settings:

```python
config["SERVER"] = "<VC_IP_Address>"
config["PASSWORD"] = "VMware1!"
config["VM_DATASTORE_NAME"] = "vsanDatastore"
```

### Run create basic VM sample

**NOTE:** Be sure to name the VM using your First and Last name so it's unique!!

```bash
python samples/vsphere/vcenter/vm/create/create_basic_vm.py -v -n "vm_<firstname_lastname>"
```

### Verify the new VM is created successfully

```bash
python samples/vsphere/vcenter/vm/list_vms.py -v
```

### Run deploy ovf template sample

**NOTE:** Use single quote for password in Mac 'VMware1!'

```bash
python samples/vsphere/contentlibrary/ovfdeploy/deploy_ovf_template.py -v -clustername "Cluster1" -libitemname "Sample_OVF"
```

### Verify the new VM is deployed successfully

```bash
python samples/vsphere/vcenter/vm/list_vms.py -v
```

## Exercises
Try to use the sample_template to create three scripts and then run them:

* Power on/off the VM you created
* Edit VM cpu/memory
* Add a CD-ROM to your VM
