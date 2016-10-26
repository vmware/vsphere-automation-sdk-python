# VMware vSphere Automation SDK for Python
## Table of Contents
* [Abstract](#abstract)
* [Table of Contents](https://github.com/vmware/vsphere-automation-sdk-java-samples#table-of-contents)
* [Getting Started](https://github.com/vmware/vsphere-automation-sdk-java-samples#getting-started)
  * [Downloading the Repository for Local Access](https://github.com/vmware/vsphere-automation-sdk-java-samples#downloading-the-repository-for-local-access)
  * [Prerequisites](https://github.com/vmware/vsphere-automation-sdk-java-samples#prerequisites)
  * [Building the Samples](https://github.com/vmware/vsphere-automation-sdk-java-samples#building-the-samples)
  * [Running the Samples](https://github.com/vmware/vsphere-automation-sdk-java-samples#running-the-samples)
* [Submitting Samples](https://github.com/vmware/vsphere-automation-sdk-java-samples#submitting-samples)
  * [Required Information](https://github.com/vmware/vsphere-automation-sdk-java-samples#required-information)
  * [Suggested Information](https://github.com/vmware/vsphere-automation-sdk-java-samples#suggested-information)
* [Resource Maintenance](https://github.com/vmware/vsphere-automation-sdk-java-samples#resource-maintenance)
  * [Maintenance Ownership](https://github.com/vmware/vsphere-automation-sdk-java-samples#maintenance-ownership)
  * [Filing issues](https://github.com/vmware/vsphere-automation-sdk-java-samples#filing-isssues)
  * [Resolving issues](https://github.com/vmware/vsphere-automation-sdk-java-samples#resolving-issues)
* [Additional Resources](https://github.com/vmware/vsphere-automation-sdk-java-samples#additional-resources)
  * [Discussions](https://github.com/vmware/vsphere-automation-sdk-java-samples#discussions)
  * [VMware Sample Exchange](https://github.com/vmware/vsphere-automation-sdk-java-samples#vmware-sample-exchange)
* [LICENSE AGREEMENT](https://github.com/vmware/vsphere-automation-sdk-java-samples#license-agreement)

## Abstract
This document for the vSphere Automation SDK for java describes -
1. How to build the java samples in this repository.
2. How to run the samples in this repository
3. The procedure for contributing new samples.

## Getting Started
### Downloading the Repository for Local Access
1. Load the GitHub repository page: <https://github.com/vmware/vsphere-automation-sdk-java-samples>
2. Click on the green “Clone or Download” button and then click “Download ZIP”  
3. Once downloaded, extract the zip file to the location of your choosing  
4. At this point, you now have a local copy of the repository

### Prerequisites
#### Required:
The below items need to be installed for building and running the samples:
* Maven 3
* JDK 8
* vCenter Server 6.5

### Building the Samples
In the root directory of your folder after cloning the repository, run the below maven commands -

`mvn initialize`

`mvn clean install`

### Running the Samples
When running the samples, parameters can be provided either on the command line, in a configuration file (using the --config-file parameter), or a combination of both. The parameter values specified on the command line will override those specified in the configuration file. When using a configuration file, each required parameter for the sample must be specified either in the configuration file or as a command line parameter. Each parameter specified in the configuration file should be in the "key=value" format. For example:

`vmname=TestVM`

`cluster=Cluster1`

Use a command like the following to display usage information for a particular sample.
```` bash
$java -cp target/samples-6.5.0-jar-with-dependencies.jar vmware.samples.tagging.workflow.TaggingWorkflow

java -cp target/samples-6.5.0-jar-with-dependencies.jar packagename.SampleClassName [--config-file <CONFIGURATION FILE>]
       --server <SERVER> --username <USERNAME> --password <PASSWORD> --cluster <CLUSTER> [--truststorepath <ABSOLUTE PATH OF JAVA TRUSTSTORE FILE>]
       [--truststorepassword <JAVA TRUSTSTORE PASSWORD>] [--cleardata] [--skip-server-verification]

Sample Options:
    --config-file <CONFIGURATION FILE>                         OPTIONAL: Absolute path to  the configuration file containing the sample options.
                                                               NOTE: Parameters can be specified either in the configuration file or on the command
                                                               line. Command line parameters will override values specified in the configuration file.
    --server <SERVER>                                          hostname of vCenter Server
    --username <USERNAME>                                      username to login to the vCenter Server
    --password <PASSWORD>                                      password to login to the vCenter Server
    --cluster <CLUSTER>                                        The name of the cluster to be tagged
    --truststorepath <ABSOLUTE PATH OF JAVA TRUSTSTORE FILE>   Specify the absolute path to the file containing the trusted server certificates. This
                                                               option can be skipped if the parameter skip-server-verification is specified.
    --truststorepassword <JAVA TRUSTSTORE PASSWORD>            Specify the password for the java truststore. This option can be skipped if the
                                                               parameter skip-server-verification is specified.
    --cleardata                                                OPTIONAL: Specify this option to undo all persistent results of running the sample.
    --skip-server-verification                                 OPTIONAL: Specify this option if you do not want to perform SSL certificate
                                                               verification.
                                                               NOTE: Circumventing SSL trust in this manner is unsafe and should not be used with
                                                               production code. This is ONLY FOR THE PURPOSE OF DEVELOPMENT ENVIRONMENT.
````

Use a command like the following to run a sample using only command line parameters:
```` bash
$java -cp target/samples-6.5.0-jar-with-dependencies.jar vmware.samples.tagging.taggingworkflow.TaggingWorkflow --server servername --username administrator@vsphere.local --password password --cluster vAPISDKCluster --cleardata true --skip-server-verification
````

Use a command like the following to run a sample using only a configuration file:
```` bash
$java -cp target/samples-6.5.0-jar-with-dependencies.jar vmware.samples.tagging.workflow.TaggingWorkflow --config-file sample.properties
````

Use the following command to run the sample using a combination of configuration file and command line parameters:
```` bash
$java -cp target/samples-6.5.0-jar-with-dependencies.jar vmware.samples.tagging.workflow.TaggingWorkflow --config-file sample.properties --cluster Cluster1
````

### API Documentation and Programming Guide
The API documentation for the samples can be found here :

The programming guide for vSphere Automation SDK for Java can be found here:  

## Submitting samples
The following information must be included in the README.md for each submitted sample.
* Author Name
  * This can include full name, email address or other identifiable piece of information that would allow interested parties to contact author with questions.
* Date
  * Date the sample was originally written
* Minimal/High Level Description
  * What does the sample do ?
* vSphere version against which the sample was developed/tested
* SDK version against which the sample was developed/tested
* Java version against which the sample was developed/tested
* Any KNOWN limitations or dependencies

## Resource Maintenance
### Maintenance Ownership
Ownership of any and all submitted samples are maintained by the submitter.
### Filing Issues
Any bugs or other issues should be filed within GitHub by way of the repository’s Issue Tracker.
### Resolving Issues
Any community member can resolve issues within the repository, however only the board member can approve the update. Once approved, assuming the resolution involves a pull request, only a board member will be able to merge and close the request.

### VMware Sample Exchange
It is highly recommended to add any and all submitted samples to the VMware Sample Exchange:  <https://developercenter.vmware.com/samples>

Sample Exchange can be allowed to access your GitHub resources, by way of a linking process, where they can be indexed and searched by the community. There are VMware social media accounts which will advertise resources posted to the site and there's no additional accounts needed, as the VMware Sample Exchange uses MyVMware credentials.     

## LICENSE AGREEMENT
License Agreement: <https://<path to license file>

# Repository Administrator Resources
## Table of Contents
* Board Members
* Approval of Additions

## Board Members

Board members are volunteers from the SDK community and VMware staff members, board members are not held responsible for any issues which may occur from running of samples from this repository.

Members:

## Approval of Additions
Items added to the repository, including items from the Board members, require 2 votes from the board members before being added to the repository. The approving members will have ideally downloaded and tested the item. When two “Approved for Merge” comments are added from board members, the pull can then be committed to the repository.
