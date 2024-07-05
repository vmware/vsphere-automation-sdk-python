# vLCM/Cluster/Installed_Images

This directory contains samples of the cluster-level vLCM installed images API

The installed images API provides a way to easily see the software running on hosts in a given cluster.  This API will scan the hosts in the target cluster and generate a report detailing what images are being run.  These images are organized into three categories: "highest versioned image", "most widely used image", and "hostImageList" which just contains the rest of the images.

## APIs
POST
   - The extract POST method triggers the installed images workflow, which is an asynchronous operation.  This API returns a task ID which can be used to monitor the progress of the task.

GET
   - This GET method is a synchronous operation and it returns the most recently generated installed images report for the cluster corresponding to the provided MoID.

## Running the samples

To view the available command-line options:

   ```
   python samples/vsphere/vcenter/vlcm/cluster/installed_images/installed_images.py -h
   ```

To run the sample:

   ```
   $ python samples/vsphere/vcenter/vlcm/cluster/installed_images/installed_images.py -v -s <vCenter server IP> -u <username> -p <password> --cluster <cluster MoID>
   ```