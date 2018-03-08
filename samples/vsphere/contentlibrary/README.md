This directory contains samples for Content Library APIs:

    * CRUD operations on a content library                                                                                  - crud/library_crud.py
    * Updating content of a content library item                                                                            - contentupdate/content_update.py
    * Workflow to deploy an OVF library item to a resource pool                                                             - ovfdeploy/deploy_ovf_template.py
    * Workflows to import an OVF package into a content library, and download of an OVF template from a content library     - ovfimport/ovf_import_export.py
    * Basic workflow to publish and subscribe content libraries                                                             - publishsubscribe/library_publish_subscribe.py
    * Workflow to capture a virtual machine into a content library                                                          - vmcapture/vm_template_capture.py
    * Content library ISO item mount and unmount workflow                                                                   - isomount/iso_mount.py
    * Create a library item containing a virtual machine template                                                           - vmtemplate/create_vm_template.py
    * Deploy a virtual machine from a library item containing a virtual machine template                                    - vmtemplate/deploy_vm_template.py

Running the samples

    $ python <sample-dir>/<sample>.py --server <vCenter Server IP> --username <username> --password <password> <additional-sample-parameters>

The additional sample parameters are as follows (all parameters can be displayed for any sample using option --help)

    * library_crud.py               --datastorename <datastore-name>
    * content_update.py             --datastorename <datastore-name>
    * deploy_ovf_template.py        --clustername <cluster-name>  --libitemname <ovf-item-name>
    * ovf_import_export.py          --datastorename <datastore-name>
    * library_publish_subscribe.py  --datastorename <datastore-name>
    * vm_template_capture.py        --datastorename <datastore-name> --vmname <vm-name>
    * iso_mount.py                  --datastorename <datastore-name> --vmname <vm-name>
    * create_vm_template.py         --datacentername <datacenter-name> --resourcepoolname <resource-pool-name> --datastorename <datastore-name> --vmname <vm-name>
    * deploy_vm_template.py         --itemname <item-name> --datacentername <datacenter-name> --foldername <folder-name>  --resourcepoolname <resource-pool-name> --datastorename <datastore-name>    

* Testbed Requirement:
    - 1 vCenter Server
    - 2 ESX hosts
    - 1 datastore
    - Some samples need a VM or an OVF library item created as mentioned above

